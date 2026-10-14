            use_container_width=True,
            hide_index=True,
            height=500,
        )

        st.download_button(
            "Download complete project record",
            data=raw_record.to_frame().T.to_csv(index=False).encode("utf-8"),
            file_name=f"sunstripe_project_{chosen_id}.csv",
            mime="text/csv",
        )

        record_url = project.get("source_url", "")

        if isinstance(record_url, str) and record_url.startswith("https://"):
            st.markdown(f"[Open source workbook]({record_url})")
        elif data_mode == "EIA live inventory":
            st.markdown(f"[Open official EIA page]({EIA_PAGE})")

        st.warning(
            "This view shows the available fields from the selected dataset. "
            "Parcel ownership, land valuation, permits, interconnection studies, "
            "storage duration and project revenue may require separate sources."
        )


# ============================================================
# TECHNOLOGY ANALYTICS
# ============================================================

with tab_analytics:
    st.markdown(
        '<div class="section-title">Technology analytics</div>',
        unsafe_allow_html=True,
    )

    if filtered.empty:
        st.info("No records available for the current filters.")
    else:
        by_state = (
            filtered.groupby("state", as_index=False)
            ["nameplate_capacity_mw"].sum()
            .sort_values("nameplate_capacity_mw", ascending=False)
            .head(15)
        )

        fig = px.bar(
            by_state,
            x="state",
            y="nameplate_capacity_mw",
            text="nameplate_capacity_mw",
            title=f"{technology_choice}: capacity by state",
            labels={
                "state": "State",
                "nameplate_capacity_mw": "Nameplate capacity (MW)",
            },
        )

        fig.update_traces(
            marker_color=RED,
            texttemplate="%{text:,.0f}",
            textposition="outside",
            textfont=dict(family=FONT, size=11, color=BLACK),
            cliponaxis=False,
        )

        fig = style_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

        by_status = (
            filtered.groupby("status", as_index=False)
            .size()
            .rename(columns={"size": "Generator records"})
            .sort_values("Generator records", ascending=False)
        )

        fig2 = px.bar(
            by_status,
            x="status",
            y="Generator records",
            text="Generator records",
            title=f"{technology_choice}: records by status",
        )

        fig2.update_traces(
            marker_color=RED,
            textposition="outside",
            textfont=dict(family=FONT, size=11, color=BLACK),
            cliponaxis=False,
        )

        fig2 = style_chart(fig2)
        st.plotly_chart(fig2, use_container_width=True)


# ============================================================
# DATA SOURCES AND LIMITATIONS
# ============================================================

with tab_method:
    st.markdown(
        '<div class="section-title">Data sources and methodology</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"""
**Current dataset:** {source_label}

**Official EIA-860M page:**  
{EIA_PAGE}

EIA's monthly inventory contains reported generator information for existing
and proposed generation. Monthly data may be preliminary and revised.

A generator-level row is not necessarily a distinct development project.
Some records may not have coordinates or reported storage energy capacity.
""")

    sources = pd.DataFrame([
        {
            "Provider": "EIA monthly inventory",
            "Purpose": "Generator records",
            "Official source": EIA_PAGE,
        },
        {
            "Provider": "EIA annual inventory",
            "Purpose": "Annual generator data",
            "Official source": "https://www.eia.gov/electricity/data/eia860/",
        },
        {
            "Provider": "NREL",
            "Purpose": "Renewable resource information",
            "Official source": "https://developer.nrel.gov/",
        },
        {
            "Provider": "USGS",
            "Purpose": "Elevation and terrain",
            "Official source": "https://www.usgs.gov/",
        },
        {
            "Provider": "FEMA",
            "Purpose": "Flood hazard information",
            "Official source": "https://www.fema.gov/flood-maps",
        },
        {
            "Provider": "USFWS",
            "Purpose": "Wetlands and ecology",
            "Official source": "https://www.fws.gov/",
        },
        {
            "Provider": "ERCOT",
            "Purpose": "Texas power market",
            "Official source": "https://www.ercot.com/",
        },
        {
            "Provider": "CAISO",
            "Purpose": "California power market",
            "Official source": "https://www.caiso.com/",
        },
        {
            "Provider": "MISO",
            "Purpose": "Regional market information",
            "Official source": "https://www.misoenergy.org/",
        },
        {
            "Provider": "PJM",
            "Purpose": "Regional market information",
            "Official source": "https://www.pjm.com/",
        },
    ])

    st.dataframe(
        sources,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Official source": st.column_config.LinkColumn(
                "Official source"
            ),
        },
    )

    status_table = pd.DataFrame([
        {"Feature": "Solar / Wind / BESS selection", "Status": "Implemented"},
        {"Feature": "Technology-aware filtering", "Status": "Implemented"},
        {"Feature": "Project-level detail", "Status": "Implemented"},
        {"Feature": "Repository CSV normalization", "Status": "Implemented"},
        {"Feature": "CSV, XLS and XLSX upload", "Status": "Implemented"},
        {"Feature": "Optional EIA workbook connector", "Status": "Internet required"},
        {"Feature": "Parcel ownership / valuation", "Status": "Not connected"},
        {"Feature": "Verified interconnection capacity", "Status": "Not connected"},
        {"Feature": "Live power-market prices", "Status": "Not connected"},
