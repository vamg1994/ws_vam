import streamlit as st
from scraper import scrape_tables, get_raw_html
from utils import validate_url, format_table_name
import pandas as pd

def main():
    st.set_page_config(
        page_title="Web Table Scraper",
        page_icon="🔍",
        layout="wide"
    )

    # Custom CSS
    with open('styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.title("🔍 Web Table Scraper")
    st.markdown("""
    Extract tables and HTML content from any webpage! Simply enter the URL below.
    """)

    # URL input
    url = st.text_input("Enter webpage URL:", placeholder="https://example.com")

    if url:
        if not validate_url(url):
            st.error("Please enter a valid URL (including http:// or https://)")
            return

        # View selection
        view_mode = st.radio(
            "Select View Mode:",
            ["Table View", "HTML View"],
            horizontal=True
        )

        if view_mode == "Table View":
            with st.spinner("Scraping tables..."):
                try:
                    tables = scrape_tables(url)
                    
                    if not tables:
                        st.warning("No tables found on the webpage!")
                        return

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

        else:  # HTML View
            with st.spinner("Fetching HTML content..."):
                try:
                    html_content = get_raw_html(url)
                    
                    # Display HTML content in a code block
                    st.code(html_content, language="html")
                    
                    # Add download button for HTML
                    st.download_button(
                        label="Download HTML",
                        data=html_content,
                        file_name=f"{format_table_name(url, 0)}.html",
                        mime="text/html"
                    )

                except Exception as e:
                    st.error(f"An error occurred while fetching HTML: {str(e)}")

if __name__ == "__main__":
    main()
