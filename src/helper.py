"""Helper Functions."""

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator


@st.cache_data(ttl="1d")
def read_data(pop: int) -> pd.DataFrame:
    """Read and prepare the data (cached)."""
    df = pd.read_csv("data/population.tsv", sep="\t").astype(int).set_index("Jahr")
    d_pop_per_year = df.to_dict()["Einwohner"]

    df = pd.read_csv("data/data.tsv", sep="\t")

    # calc people from percent
    df.loc[df["Personen"].isna(), "Personen"] = (
        df["Prozent"] * 0.01 * df["Jahr"].map(d_pop_per_year.get)
    ).round(0)

    # calc percent from people, no rounding here because of Dorf calc
    df.loc[df["Prozent"].isna(), "Prozent"] = (
        100 * df["Personen"] / df["Jahr"].map(d_pop_per_year.get)
    )

    # convert to village population (float without rounding here to prevent 2x rounding)
    df["Dorf"] = pop / 100 * df["Prozent"]
    return df


def print_table_simple(
    df: pd.DataFrame, col: DeltaGenerator, *, show_source: bool
) -> None:
    """Display simple table of few columns."""
    df = df.sort_values(["Prozent", "Titel"], ascending=[False, True])
    df["Dorf"] = df["Dorf"].round(0)
    col_order = ["Titel", "Dorf"]
    if show_source:
        col_order.append("Quelle")
    col.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        column_order=col_order,
        column_config={
            "Title": st.column_config.Column("Title", width="small"),
            "Dorf": st.column_config.ProgressColumn(
                label="Personen im Dorf",
                format="%d",
                min_value=0,
                max_value=df["Dorf"].max(),
                # width="large", # breaks mobile layout
            ),
            "Quelle": st.column_config.LinkColumn("Quelle", display_text="Link"),
        },
    )


def print_table_complete(df: pd.DataFrame) -> None:
    """Display complete data table."""
    df["Prozent"] = df["Prozent"].round(2)
    df["Dorf"] = df["Dorf"].round(1)
    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        column_order=[
            "Kategorie",
            "Titel",
            "Personen",
            "Prozent",
            "Dorf",
            "Quelle",
            "Jahr",
            "Kommentar",
        ],
        column_config={
            "Quelle": st.column_config.LinkColumn("Quelle", display_text="Link"),
            "Jahr": st.column_config.NumberColumn("Jahr", format="%d"),
            "Dorf": st.column_config.NumberColumn("Im Dorf", format="%.1f"),
            "Prozent": st.column_config.ProgressColumn(
                format="%.2f",
                min_value=0,
                max_value=100,
                # width="large" # breaks mobile layout
            ),
        },
    )


def include_matomo_stats() -> None:
    """Include Matomo access stats update JavaScript snippet."""
    import streamlit.components.v1 as components

    components.html(
        """
<script>
var _paq = window._paq = window._paq || [];
_paq.push(['trackPageView']);
_paq.push(['enableLinkTracking']);
(function() {
    var u="https://entorb.net/stats/matomo/";
    _paq.push(['setTrackerUrl', u+'matomo.php']);
    _paq.push(['setSiteId', '7']);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
})();
</script>
    """,
        height=0,
    )
