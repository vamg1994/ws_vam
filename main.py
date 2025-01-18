import streamlit as st
from scraper import scrape_tables, get_raw_html, get_all_urls, get_colors, get_images, analyze_performance, analyze_seo
from utils import validate_url, format_table_name
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import plotly.express as px

def main():
    st.set_page_config(
        page_title="VAM Web Scraper",
        page_icon="🔍",
        layout="wide"
    )

    # Custom CSS
    with open('styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.title("🔍 VAM Web Scraper")
    st.markdown("""
    Extract tables, HTML, URLs from any webpage!
    """)

    # Sidebar content
    with st.sidebar:
        # URL input
        url = st.text_input("Enter webpage URL:", placeholder="https://example.com")
        
        st.markdown("---")  # Divider
        
        # Contact links
        st.markdown("### Virgilio Madrid - Data Scientist")
        st.link_button("Portfolio 🌐", "https://portfolio-vam.vercel.app/")
        st.link_button("LinkedIn 💼", "https://www.linkedin.com/in/vamadrid/")
        st.link_button("E-Mail 📧", "mailto:virgiliomadrid1994@gmail.com")

    # Main content with tabs
    table_tab, html_tab, url_tab, color_tab, image_tab, perf_tab, seo_tab = st.tabs([
        "📊 Table View", "🗎 HTML View", "🔗 URL Explorer", "🎨 Colors", "🖼️ Images", "⚡ Performance", "🎯 SEO Analysis"
    ])

    with table_tab:
        if not url:
            st.info("Enter a URL in the sidebar to start scraping tables!")
        elif not validate_url(url):
            st.error("Please enter a valid URL (including http:// or https://)")
        else:
            if st.button("Scrape Tables", key="scrape_tables_btn", type="primary"):
                with st.spinner("Scraping tables..."):
                    try:
                        tables = scrape_tables(url)
                        
                        if not tables:
                            st.warning("No tables found on the webpage!")
                        else:
                            st.success(f"Found {len(tables)} table(s)!")

                            # Display each table with download option
                            for idx, table in enumerate(tables):
                                with st.expander(f"Table {idx + 1}", expanded=True):
                                    st.dataframe(table)
                                    
                                    # Convert to CSV for download
                                    csv = table.to_csv(index=False)
                                    table_name = format_table_name(url, idx)
                                    
                                    st.download_button(
                                        label="Download CSV",
                                        data=csv,
                                        file_name=f"{table_name}.csv",
                                        mime="text/csv"
                                    )

                    except Exception as e:
                        st.error(f"An error occurred while scraping tables: {str(e)}")

    with html_tab:
        if not url:
            st.info("Enter a URL in the sidebar to view HTML content!")
        elif not validate_url(url):
            st.error("Please enter a valid URL (including http:// or https://)")
        else:
            if st.button("Fetch HTML", key="fetch_html_btn", type="primary"):
                with st.spinner("Fetching HTML content..."):
                    try:
                        html_content = get_raw_html(url)
                        if html_content:
                            # Display HTML content in a code block
                            st.code(html_content, language="html")
                            
                            # Add download button for HTML
                            st.download_button(
                                label="Download HTML",
                                data=html_content,
                                file_name="webpage.html",
                                mime="text/html"
                            )
                        else:
                            st.warning("No HTML content found!")

                    except Exception as e:
                        st.error(f"An error occurred while fetching HTML: {str(e)}")

    with url_tab:
        if not url:
            st.info("Enter a URL in the sidebar to explore all links!")
        elif not validate_url(url):
            st.error("Please enter a valid URL (including http:// or https://)")
        else:
            if st.button("Scrape URLs", key="scrape_urls_btn", type="primary"):
                with st.spinner("Scraping URLs..."):
                    try:
                        # Get all URLs from the webpage
                        urls_df = get_all_urls(url)
                        
                        if urls_df.empty:
                            st.warning("No URLs found on the webpage!")
                        else:
                            st.success(f"Found {len(urls_df)} URL(s)!")
                            # Store URLs in session state for filtering
                            st.session_state.urls = urls_df

                    except Exception as e:
                        st.error(f"An error occurred while scraping URLs: {str(e)}")

            # Show filters and URLs if we have URLs in session state
            if hasattr(st.session_state, 'urls') and not st.session_state.urls.empty:
                # Add filter options
                st.subheader("Filter URLs")
                col1, col2 = st.columns([2, 1])
                with col1:
                    filter_text = st.text_input(
                        "Filter URLs containing:",
                        placeholder="Enter text to filter URLs...",
                        help="Filter URLs that contain specific text (case-insensitive)"
                    )
                with col2:
                    link_type = st.selectbox(
                        "Filter by type:",
                        options=["All"] + sorted(st.session_state.urls['type'].unique().tolist()),
                        help="Filter URLs by link type"
                    )

                # Apply filters
                filtered_df = st.session_state.urls.copy()
                
                # Text filter
                if filter_text:
                    mask = (
                        filtered_df['url'].str.contains(filter_text, case=False, na=False) |
                        filtered_df['text'].str.contains(filter_text, case=False, na=False)
                    )
                    filtered_df = filtered_df[mask]
                
                # Type filter
                if link_type != "All":
                    filtered_df = filtered_df[filtered_df['type'] == link_type]

                st.markdown(f"**Showing {len(filtered_df)} filtered results**")

                # Display URLs table with additional columns
                st.dataframe(
                    filtered_df,
                    column_config={
                        "url": st.column_config.LinkColumn("URL"),
                        "text": "Link Text",
                        "type": "Link Type"
                    },
                    hide_index=True,
                    use_container_width=True
                )

                # Download button for URLs
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download URLs as CSV",
                    data=csv,
                    file_name=f"urls_{format_table_name(url, 0)}.csv",
                    mime="text/csv"
                )

    with color_tab:
        if not url:
            st.info("Enter a URL in the sidebar to extract colors!")
        elif not validate_url(url):
            st.error("Please enter a valid URL (including http:// or https://)")
        else:
            if st.button("Extract Colors", key="extract_colors_btn", type="primary"):
                with st.spinner("Extracting colors..."):
                    try:
                        colors = get_colors(url)
                        
                        if not colors:
                            st.warning("No colors found on the webpage!")
                        else:
                            st.success(f"Found {len(colors)} unique color(s)!")

                            # Separate colors by format
                            hex_colors = [c for c in colors if c['format'] == 'hex']
                            rgb_colors = [c for c in colors if c['format'] in ['rgb', 'rgba']]

                            # Display HEX colors
                            if hex_colors:
                                st.subheader("🎨 HEX Colors")
                                cols = st.columns(4)
                                for idx, color_info in enumerate(hex_colors):
                                    col_idx = idx % 4
                                    with cols[col_idx]:
                                        color = color_info['color']
                                        st.markdown(
                                            f"""
                                            <div style="
                                                background-color: {color};
                                                width: 100%;
                                                height: 50px;
                                                border-radius: 5px;
                                                margin: 5px 0;
                                                border: 1px solid #ccc;
                                            "></div>
                                            <code>{color}</code>
                                            <p><small>Source: {color_info['source']}</small></p>
                                            """,
                                            unsafe_allow_html=True
                                        )

                            # Display RGB/RGBA colors
                            if rgb_colors:
                                st.subheader("🎨 RGB/RGBA Colors")
                                cols = st.columns(4)
                                for idx, color_info in enumerate(rgb_colors):
                                    col_idx = idx % 4
                                    with cols[col_idx]:
                                        color = color_info['color']
                                        st.markdown(
                                            f"""
                                            <div style="
                                                background-color: {color};
                                                width: 100%;
                                                height: 50px;
                                                border-radius: 5px;
                                                margin: 5px 0;
                                                border: 1px solid #ccc;
                                            "></div>
                                            <code>{color}</code>
                                            <p><small>Source: {color_info['source']}</small></p>
                                            """,
                                            unsafe_allow_html=True
                                        )

                            # Create DataFrame for download
                            color_df = pd.DataFrame(colors)
                            
                            # Add download button
                            csv = color_df.to_csv(index=False)
                            st.download_button(
                                label="Download Colors as CSV",
                                data=csv,
                                file_name=f"colors_{format_table_name(url, 0)}.csv",
                                mime="text/csv"
                            )

                    except Exception as e:
                        st.error(f"An error occurred while extracting colors: {str(e)}")

    with image_tab:
        if not url:
            st.info("Enter a URL in the sidebar to extract images!")
        elif not validate_url(url):
            st.error("Please enter a valid URL (including http:// or https://)")
        else:
            if st.button("Extract Images", key="extract_images_btn", type="primary"):
                with st.spinner("Extracting images..."):
                    try:
                        images = get_images(url)
                        
                        if not images:
                            st.warning("No images found on the webpage!")
                        else:
                            st.success(f"Found {len(images)} image(s)!")

                            # Store images in session state for filtering
                            st.session_state.images = images

                    except Exception as e:
                        st.error(f"An error occurred while extracting images: {str(e)}")

            # Show filters and images if we have images in session state
            if hasattr(st.session_state, 'images') and st.session_state.images:
                # Filter options
                col1, col2 = st.columns([2, 1])
                with col1:
                    filter_text = st.text_input(
                        "Filter by alt text or URL:",
                        placeholder="Enter text to filter images...",
                        help="Filter images by their alt text or URL"
                    )
                with col2:
                    image_types = list(set(img['type'] for img in st.session_state.images))
                    selected_type = st.selectbox(
                        "Filter by type:",
                        options=["All"] + sorted(image_types),
                        help="Filter images by file type"
                    )

                # Apply filters
                filtered_images = st.session_state.images
                if filter_text:
                    filtered_images = [
                        img for img in filtered_images
                        if (filter_text.lower() in img['alt'].lower() or 
                            filter_text.lower() in img['url'].lower() or
                            filter_text.lower() in img['title'].lower())
                    ]
                if selected_type != "All":
                    filtered_images = [
                        img for img in filtered_images
                        if img['type'] == selected_type
                    ]

                st.markdown(f"**Showing {len(filtered_images)} filtered images**")

                # Display images in a grid
                cols = st.columns(3)
                for idx, img_data in enumerate(filtered_images):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        try:
                            if not img_data['url'].startswith('data:'):
                                st.image(
                                    img_data['url'],
                                    caption=f"Alt: {img_data['alt']}\nSize: {img_data['width']}x{img_data['height']}",
                                    use_container_width=True
                                )
                            else:
                                st.info("Base64 encoded image")
                            
                            # Add copy URL button
                            st.code(img_data['url'], language=None)
                            st.markdown(f"Type: {img_data['type']}")
                            
                        except Exception as e:
                            st.error(f"Failed to load image: {str(e)}")

    with perf_tab:
        if not url:
            st.info("Enter a URL in the sidebar to analyze performance!")
        elif not validate_url(url):
            st.error("Please enter a valid URL (including http:// or https://)")
        else:
            if st.button("Analyze Performance", key="analyze_perf_btn", type="primary"):
                with st.spinner("Analyzing webpage performance..."):
                    try:
                        perf_data = analyze_performance(url)
                        
                        # Display key metrics in columns
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Response Time", f"{perf_data['response_time']}s")
                        with col2:
                            st.metric("Total Size", f"{perf_data['total_page_weight']:.2f} KB")
                        with col3:
                            st.metric("Resources", perf_data['total_resources'])

                        # Resource Distribution Chart
                        st.subheader("Resource Distribution")
                        resource_df = pd.DataFrame({
                            'Type': list(perf_data['resources'].keys()),
                            'Count': list(perf_data['resources'].values())
                        })
                        fig = px.pie(
                            resource_df,
                            values='Count',
                            names='Type',
                            title='Resource Distribution by Type'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # Resource Sizes Chart
                        st.subheader("Resource Sizes (KB)")
                        sizes_df = pd.DataFrame({
                            'Type': list(perf_data['resource_sizes'].keys()),
                            'Size (KB)': list(perf_data['resource_sizes'].values())
                        })
                        fig = px.bar(
                            sizes_df,
                            x='Type',
                            y='Size (KB)',
                            title='Resource Sizes by Type'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # Technical Details
                        with st.expander("Technical Details"):
                            st.json({
                                'Status Code': perf_data['status_code'],
                                'Content Type': perf_data['content_type'],
                                'Encoding': perf_data['encoding'],
                                'Compression': perf_data['compression'],
                                'Cache Control': perf_data['cache_control'],
                                'Server': perf_data['server']
                            })

                        # Response Headers
                        with st.expander("Response Headers"):
                            st.json(perf_data['headers'])

                    except Exception as e:
                        st.error(f"An error occurred while analyzing performance: {str(e)}")

    with seo_tab:
        if not url:
            st.info("Enter a URL in the sidebar to analyze SEO!")
        elif not validate_url(url):
            st.error("Please enter a valid URL (including http:// or https://)")
        else:
            if st.button("Analyze SEO", key="analyze_seo_btn", type="primary"):
                with st.spinner("Analyzing webpage SEO..."):
                    try:
                        seo_data = analyze_seo(url)
                        
                        # Meta Information
                        st.subheader("📋 Meta Information")
                        meta_col1, meta_col2 = st.columns(2)
                        
                        with meta_col1:
                            st.markdown("**Title**")
                            st.code(seo_data['meta_tags'].get('title', 'Not found'))
                            
                            st.markdown("**Description**")
                            st.code(seo_data['meta_tags'].get('description', 'Not found'))
                        
                        with meta_col2:
                            st.markdown("**Language**")
                            st.code(seo_data['lang'])
                            
                            st.markdown("**Robots Directive**")
                            st.code(seo_data['robots_meta'])

                        # Headings Structure
                        st.subheader("📑 Heading Structure")
                        for level, headings in seo_data['headings'].items():
                            if headings:
                                with st.expander(f"{level.upper()} Tags ({len(headings)})"):
                                    for h in headings:
                                        st.markdown(f"- {h}")

                        # Content Stats
                        st.subheader("📊 Content Statistics")
                        stats_col1, stats_col2, stats_col3 = st.columns(3)
                        
                        with stats_col1:
                            st.metric("Word Count", seo_data['word_count'])
                        with stats_col2:
                            st.metric("Text/HTML Ratio", f"{seo_data['text_html_ratio']}%")
                        with stats_col3:
                            total_headings = sum(len(h) for h in seo_data['headings'].values())
                            st.metric("Total Headings", total_headings)

                        # Images Analysis
                        st.subheader("🖼️ Image Optimization")
                        img_col1, img_col2 = st.columns(2)
                        with img_col1:
                            st.metric("Images with Alt Text", seo_data['images']['with_alt'])
                        with img_col2:
                            st.metric("Images without Alt Text", seo_data['images']['without_alt'])

                        # Links Analysis
                        st.subheader("🔗 Link Analysis")
                        link_col1, link_col2, link_col3 = st.columns(3)
                        with link_col1:
                            st.metric("Internal Links", seo_data['links']['internal'])
                        with link_col2:
                            st.metric("External Links", seo_data['links']['external'])
                        with link_col3:
                            st.metric("Nofollow Links", seo_data['links']['nofollow'])

                        # Technical SEO
                        st.subheader("⚙️ Technical SEO")
                        tech_col1, tech_col2 = st.columns(2)
                        
                        with tech_col1:
                            st.markdown("**Canonical URL**")
                            st.code(seo_data['canonical_url'] or 'Not specified')
                            
                            st.markdown("**Viewport Setting**")
                            st.code(seo_data['viewport'])
                        
                        with tech_col2:
                            if seo_data['structured_data']:
                                st.markdown("**Structured Data**")
                                for data in seo_data['structured_data']:
                                    with st.expander("View Structured Data"):
                                        st.json(data)

                    except Exception as e:
                        st.error(f"An error occurred while analyzing SEO: {str(e)}")






if __name__ == "__main__":
    main()
