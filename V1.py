import datetime as dt
import html
import re
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st
from snowflake.snowpark import Session


TABLE_NAME = "DB_CORE_PRD.PSG.ABOVE_STORE_USER_GROUP_MEMBERS"
COLES_RED = "#E50016"
COLES_BLACK = "#000000"
TIMESTAMP_SQL_FORMAT = "YYYY-MM-DD HH24:MI:SS.FF9"

GROUP_OPTIONS = [
    "BIP_RepPilot_Consumer",
    "BIP_SpaceRange_Consumer",
    "BIP_StockMgmt_Consumer",
    "BIP_StoreSupport_Consumer",
    "BIP_CUST_TXN_Consumer",
    "BIP_CUST_TXN_Author",
    "BIP_DCLoadVal_Consumer",
    "BIP_ProdFin_Consumer",
]

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+\-']+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


st.set_page_config(page_title="BIP Access Manager", layout="wide")


def apply_theme() -> None:
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMainBlockContainer"],
.main, .block-container {{
    background: {COLES_BLACK} !important;
    color: #f8fafc !important;
}}

[data-testid="stHeader"] {{
    background: transparent !important;
}}

.block-container {{
    padding-top: 1.1rem !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
}}

p, span, label, div, li, h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdown"], [data-testid="stMarkdown"] * {{
    color: #f8fafc !important;
}}

h1, h2, h3, .red-text {{
    color: {COLES_RED} !important;
}}

.app-header {{
    background: linear-gradient(135deg, #060000 0%, #190003 60%, #2b0005 100%);
    border: 1px solid rgba(229, 0, 22, 0.72);
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 16px;
}}

.app-title {{
    color: {COLES_RED} !important;
    font-size: 28px;
    line-height: 1.1;
    font-weight: 700;
    letter-spacing: -0.5px;
}}

.app-subtitle {{
    color: #cbd5e1 !important;
    font-size: 12px;
    margin-top: 6px;
}}

.section-label {{
    color: {COLES_RED} !important;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    margin: 16px 0 8px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(229, 0, 22, 0.42);
}}

.metric-card {{
    background: #090909;
    border: 1px solid #262626;
    border-left: 4px solid {COLES_RED};
    border-radius: 10px;
    padding: 14px 16px;
}}

.metric-value {{
    color: {COLES_RED} !important;
    font-size: 24px;
    font-weight: 700;
    margin: 0 !important;
}}

.metric-label {{
    color: #94a3b8 !important;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin: 4px 0 0 0 !important;
    text-transform: uppercase;
}}

[data-testid="stTabs"] button {{
    background: transparent !important;
    color: #94a3b8 !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    letter-spacing: 0.4px !important;
    text-transform: uppercase !important;
}}

[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {COLES_RED} !important;
    border-bottom: 3px solid {COLES_RED} !important;
}}

[data-testid="stTextInput"] label,
[data-testid="stDateInput"] label,
[data-testid="stTimeInput"] label,
[data-testid="stCheckbox"] label,
[data-testid="stSelectbox"] label,
[data-testid="stTextArea"] label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] * {{
    color: {COLES_RED} !important;
    font-weight: 600 !important;
}}

input, textarea,
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input,
[data-baseweb="input"] input,
[data-baseweb="select"] > div {{
    background: #0b0b0b !important;
    color: #f8fafc !important;
    border: 1px solid #333333 !important;
    border-radius: 7px !important;
}}

input:focus, textarea:focus {{
    border-color: {COLES_RED} !important;
    box-shadow: 0 0 0 1px {COLES_RED} !important;
}}

input::placeholder, textarea::placeholder {{
    color: #64748b !important;
}}

[data-baseweb="popover"], [data-baseweb="popover"] > div,
[data-baseweb="menu"], [data-baseweb="menu"] li,
ul[role="listbox"], ul[role="listbox"] li,
[role="option"] {{
    background: #0b0b0b !important;
    color: #f8fafc !important;
}}

button,
[data-testid="baseButton-secondary"],
[data-testid="baseButton-primary"],
[data-testid="stDownloadButton"] button {{
    background: {COLES_RED} !important;
    color: #ffffff !important;
    border: 1px solid {COLES_RED} !important;
    border-radius: 7px !important;
    font-weight: 700 !important;
}}

button:hover,
[data-testid="baseButton-secondary"]:hover,
[data-testid="baseButton-primary"]:hover,
[data-testid="stDownloadButton"] button:hover {{
    background: #ff1f33 !important;
    border-color: #ff1f33 !important;
    color: #ffffff !important;
}}

button:disabled, button[disabled] {{
    background: #3a3a3a !important;
    border-color: #3a3a3a !important;
    color: #9ca3af !important;
}}

[data-testid="stDataFrame"] {{
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid #262626 !important;
}}

[data-testid="stDataFrame"] > div {{
    --gdg-bg-cell: #050505 !important;
    --gdg-bg-header: #111111 !important;
    --gdg-text-dark: #f8fafc !important;
    --gdg-text-medium: #cbd5e1 !important;
    --gdg-text-light: #94a3b8 !important;
    --gdg-text-header: {COLES_RED} !important;
    --gdg-border-color: #262626 !important;
    --gdg-horizontal-border-color: #262626 !important;
    --gdg-accent-color: {COLES_RED} !important;
    --gdg-accent-light: rgba(229, 0, 22, 0.18) !important;
}}

[data-testid="stAlert"], [role="alert"] {{
    background: #0b0b0b !important;
    color: #f8fafc !important;
    border: 1px solid #262626 !important;
    border-left: 4px solid {COLES_RED} !important;
}}

hr {{
    border-color: #262626 !important;
}}

.small-muted {{
    color: #94a3b8 !important;
    font-size: 12px;
}}
</style>
""",
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def get_session() -> Session:
    return Session.builder.getOrCreate()


def normalize_email(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", "", str(value).strip().lower())


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.match(normalize_email(value)))


def sql_escape(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("'", "''")


def html_escape(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return html.escape(str(value))


def timestamp_literal(value: dt.datetime) -> str:
    return (
        "TO_TIMESTAMP_NTZ("
        f"'{value.strftime('%Y-%m-%d %H:%M:%S.%f')}', "
        "'YYYY-MM-DD HH24:MI:SS.FF6'"
        ")"
    )


def combine_date_time(date_value: dt.date, time_value: dt.time) -> Optional[dt.datetime]:
    if date_value is None or time_value is None:
        return None
    if isinstance(time_value, dt.datetime):
        time_value = time_value.time()
    return dt.datetime.combine(date_value, time_value.replace(tzinfo=None))


def safe_to_datetime(value: Any) -> Optional[dt.datetime]:
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(value, dt.datetime):
        return value.replace(tzinfo=None)

    if isinstance(value, dt.date):
        return dt.datetime.combine(value, dt.time.min)

    try:
        parsed = pd.to_datetime(value)
        if pd.isna(parsed):
            return None
        return parsed.to_pydatetime().replace(tzinfo=None)
    except Exception:
        return None


def format_display_datetime(value: Any) -> str:
    parsed = safe_to_datetime(value)
    if not parsed:
        return ""
    return parsed.strftime("%d %b %Y %I:%M %p")


def get_current_user_email(session: Session) -> str:
    try:
        user_info = getattr(st, "user", None)
        if user_info:
            if hasattr(user_info, "get"):
                email = user_info.get("email")
            else:
                email = getattr(user_info, "email", None)

            email = normalize_email(email)
            if email:
                return email
    except Exception:
        pass

    try:
        snowflake_user = session.sql("SELECT CURRENT_USER()").to_pandas().iloc[0, 0]
        snowflake_user = normalize_email(snowflake_user)
        return snowflake_user or "unknown"
    except Exception:
        return "unknown"


def run_df(session: Session, sql: str) -> pd.DataFrame:
    return session.sql(sql).to_pandas()


def show_metric(label: str, value: int) -> None:
    st.markdown(
        f"""
<div class="metric-card">
    <p class="metric-value">{int(value)}</p>
    <p class="metric-label">{html_escape(label)}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def status_sql() -> str:
    return """
        CASE
            WHEN TO_DATE <= CURRENT_TIMESTAMP() THEN 'Expired'
            WHEN FROM_DATE > CURRENT_TIMESTAMP() THEN 'Scheduled'
            WHEN FROM_DATE <= CURRENT_TIMESTAMP() AND TO_DATE > CURRENT_TIMESTAMP() THEN 'Active'
            ELSE 'Expired'
        END
    """


def access_query(search_email: str = "", active_only: bool = False, limit: int = 300) -> str:
    safe_search = sql_escape(normalize_email(search_email))
    where_parts = ["1 = 1"]

    if safe_search:
        where_parts.append(f"LOWER(UPN) LIKE '%{safe_search}%'")

    if active_only:
        where_parts.append("FROM_DATE <= CURRENT_TIMESTAMP()")
        where_parts.append("TO_DATE > CURRENT_TIMESTAMP()")

    where_sql = " AND ".join(where_parts)

    return f"""
        SELECT
            UPN AS "Email",
            USER_GROUP_NAME AS "Group",
            FROM_DATE AS "From Date",
            TO_DATE AS "To Date",
            {status_sql()} AS "Status",
            CREATED_BY AS "Created By",
            CREATED_TS AS "Created At",
            UPDATED_BY AS "Updated By",
            UPDATED_TS AS "Updated At",
            TO_VARCHAR(FROM_DATE, '{TIMESTAMP_SQL_FORMAT}') AS "From Key",
            TO_VARCHAR(TO_DATE, '{TIMESTAMP_SQL_FORMAT}') AS "To Key",
            TO_VARCHAR(CREATED_TS, '{TIMESTAMP_SQL_FORMAT}') AS "Created Key"
        FROM {TABLE_NAME}
        WHERE {where_sql}
        ORDER BY LOWER(UPN), USER_GROUP_NAME, FROM_DATE DESC
        LIMIT {int(limit)}
    """


def get_access_records(session: Session, search_email: str = "", active_only: bool = False, limit: int = 300) -> pd.DataFrame:
    return run_df(session, access_query(search_email, active_only, limit))


def display_access_table(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No access found.")
        return

    display_df = df.copy()

    for column in ["From Date", "To Date", "Created At", "Updated At", "Existing From", "Existing To"]:
        if column in display_df.columns:
            display_df[column] = display_df[column].apply(format_display_datetime)

    hidden_columns = ["From Key", "To Key", "Created Key"]
    display_df = display_df.drop(columns=[c for c in hidden_columns if c in display_df.columns], errors="ignore")

    st.dataframe(display_df, use_container_width=True, hide_index=True)


def access_counts(df: pd.DataFrame) -> Dict[str, int]:
    if df.empty or "Status" not in df.columns:
        return {"total": 0, "active": 0, "scheduled": 0, "expired": 0}

    status = df["Status"].fillna("")
    return {
        "total": int(len(df)),
        "active": int((status == "Active").sum()),
        "scheduled": int((status == "Scheduled").sum()),
        "expired": int((status == "Expired").sum()),
    }


def find_overlaps(
    session: Session,
    upn: str,
    groups: List[str],
    from_dt: dt.datetime,
    to_dt: dt.datetime,
    exclude_email: Optional[str] = None,
    exclude_group: Optional[str] = None,
    exclude_created_key: Optional[str] = None,
) -> pd.DataFrame:
    safe_upn = sql_escape(normalize_email(upn))
    group_values = ", ".join(f"'{sql_escape(group)}'" for group in groups)

    exclude_sql = ""
    if exclude_email and exclude_group and exclude_created_key:
        exclude_sql = f"""
          AND NOT (
              LOWER(UPN) = '{sql_escape(normalize_email(exclude_email))}'
              AND USER_GROUP_NAME = '{sql_escape(exclude_group)}'
              AND COALESCE(TO_VARCHAR(CREATED_TS, '{TIMESTAMP_SQL_FORMAT}'), '') = '{sql_escape(exclude_created_key)}'
          )
        """

    return run_df(
        session,
        f"""
        SELECT
            UPN AS "Email",
            USER_GROUP_NAME AS "Group",
            FROM_DATE AS "Existing From",
            TO_DATE AS "Existing To",
            {status_sql()} AS "Status"
        FROM {TABLE_NAME}
        WHERE LOWER(UPN) = '{safe_upn}'
          AND USER_GROUP_NAME IN ({group_values})
          AND FROM_DATE < {timestamp_literal(to_dt)}
          AND TO_DATE > {timestamp_literal(from_dt)}
          {exclude_sql}
        ORDER BY USER_GROUP_NAME, FROM_DATE
        """,
    )


def insert_access_rows(
    session: Session,
    upn: str,
    groups: List[str],
    from_dt: dt.datetime,
    to_dt: dt.datetime,
    created_by: str,
) -> None:
    safe_upn = sql_escape(normalize_email(upn))
    safe_created_by = sql_escape(normalize_email(created_by) or "unknown")

    value_rows = []
    for group in groups:
        safe_group = sql_escape(group)
        value_rows.append(
            f"('{safe_upn}', '{safe_group}', {timestamp_literal(from_dt)}, "
            f"{timestamp_literal(to_dt)}, CURRENT_TIMESTAMP(), '{safe_created_by}', NULL, NULL)"
        )

    values_sql = ",\n".join(value_rows)

    try:
        session.sql("BEGIN").collect()
        session.sql(
            f"""
            INSERT INTO {TABLE_NAME}
                (UPN, USER_GROUP_NAME, FROM_DATE, TO_DATE, CREATED_TS, CREATED_BY, UPDATED_TS, UPDATED_BY)
            SELECT
                column1,
                column2,
                column3,
                column4,
                column5,
                column6,
                column7,
                column8
            FROM VALUES
                {values_sql}
            """
        ).collect()
        session.sql("COMMIT").collect()
    except Exception:
        try:
            session.sql("ROLLBACK").collect()
        except Exception:
            pass
        raise


def update_access_window(
    session: Session,
    row: pd.Series,
    from_dt: dt.datetime,
    to_dt: dt.datetime,
    updated_by: str,
) -> int:
    safe_upn = sql_escape(normalize_email(row["Email"]))
    safe_group = sql_escape(row["Group"])
    safe_created_key = sql_escape(row["Created Key"])
    safe_updated_by = sql_escape(normalize_email(updated_by) or "unknown")

    result = session.sql(
        f"""
        UPDATE {TABLE_NAME}
        SET
            FROM_DATE = {timestamp_literal(from_dt)},
            TO_DATE = {timestamp_literal(to_dt)},
            UPDATED_TS = CURRENT_TIMESTAMP(),
            UPDATED_BY = '{safe_updated_by}'
        WHERE LOWER(UPN) = '{safe_upn}'
          AND USER_GROUP_NAME = '{safe_group}'
          AND COALESCE(TO_VARCHAR(CREATED_TS, '{TIMESTAMP_SQL_FORMAT}'), '') = '{safe_created_key}'
        """
    ).collect()

    if result and hasattr(result[0], "as_dict"):
        row_data = result[0].as_dict()
        for key in ("number of rows updated", "rows_updated", "ROWS_UPDATED"):
            if key in row_data:
                return int(row_data[key])

    return 1


def expire_access_row(session: Session, row: pd.Series, updated_by: str) -> int:
    safe_upn = sql_escape(normalize_email(row["Email"]))
    safe_group = sql_escape(row["Group"])
    safe_created_key = sql_escape(row["Created Key"])
    safe_updated_by = sql_escape(normalize_email(updated_by) or "unknown")

    result = session.sql(
        f"""
        UPDATE {TABLE_NAME}
        SET
            TO_DATE = CURRENT_TIMESTAMP(),
            UPDATED_TS = CURRENT_TIMESTAMP(),
            UPDATED_BY = '{safe_updated_by}'
        WHERE LOWER(UPN) = '{safe_upn}'
          AND USER_GROUP_NAME = '{safe_group}'
          AND COALESCE(TO_VARCHAR(CREATED_TS, '{TIMESTAMP_SQL_FORMAT}'), '') = '{safe_created_key}'
          AND TO_DATE > CURRENT_TIMESTAMP()
        """
    ).collect()

    if result and hasattr(result[0], "as_dict"):
        row_data = result[0].as_dict()
        for key in ("number of rows updated", "rows_updated", "ROWS_UPDATED"):
            if key in row_data:
                return int(row_data[key])

    return 1


def selected_groups_from_checkboxes(prefix: str) -> List[str]:
    selected = []
    cols = st.columns(2)

    for idx, group in enumerate(GROUP_OPTIONS):
        with cols[idx % 2]:
            if st.checkbox(group, key=f"{prefix}_{group}"):
                selected.append(group)

    return selected


def validate_window(from_dt: Optional[dt.datetime], to_dt: Optional[dt.datetime]) -> Optional[str]:
    if from_dt is None or to_dt is None:
        return "From date time and To date time are required."

    if from_dt >= to_dt:
        return "From date time must be before To date time."

    return None


def build_row_label(row: pd.Series) -> str:
    return (
        f"{row['Email']} | {row['Group']} | "
        f"{format_display_datetime(row['From Date'])} to {format_display_datetime(row['To Date'])} | "
        f"{row['Status']}"
    )


def render_header(current_user_email: str) -> None:
    st.markdown(
        f"""
<div class="app-header">
    <div class="app-title">BIP Access Manager</div>
    <div class="app-subtitle">Signed in as {html_escape(current_user_email)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_view_tab(session: Session) -> None:
    st.markdown('<div class="section-label">Search</div>', unsafe_allow_html=True)

    search_email = st.text_input("User email", key="view_search_email", placeholder="name@coles.com")
    active_only = st.checkbox("Active only", value=True, key="view_active_only")

    if not search_email.strip():
        st.markdown('<span class="small-muted">Enter an email address to view access.</span>', unsafe_allow_html=True)
        return

    try:
        df = get_access_records(session, search_email=search_email, active_only=active_only, limit=300)
    except Exception as exc:
        st.error(f"Failed to load access: {exc}")
        return

    counts = access_counts(df)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        show_metric("Total", counts["total"])
    with c2:
        show_metric("Active", counts["active"])
    with c3:
        show_metric("Scheduled", counts["scheduled"])
    with c4:
        show_metric("Expired", counts["expired"])

    st.markdown('<div class="section-label">Access</div>', unsafe_allow_html=True)
    display_access_table(df)


def render_provision_tab(session: Session, current_user_email: str) -> None:
    with st.form("provision_form", clear_on_submit=False):
        st.markdown('<div class="section-label">User</div>', unsafe_allow_html=True)
        upn = st.text_input("User email", placeholder="name@coles.com", key="provision_upn")

        st.markdown('<div class="section-label">Groups</div>', unsafe_allow_html=True)
        selected_groups = selected_groups_from_checkboxes("provision_group")

        st.markdown('<div class="section-label">Access Window</div>', unsafe_allow_html=True)
        now = dt.datetime.now()
        default_to = now + dt.timedelta(days=30)

        d1, t1, d2, t2 = st.columns(4)

        with d1:
            from_date = st.date_input("From date", value=now.date(), key="provision_from_date")
        with t1:
            from_time = st.time_input("From time", value=dt.time(9, 0), step=900, key="provision_from_time")
        with d2:
            to_date = st.date_input("To date", value=default_to.date(), key="provision_to_date")
        with t2:
            to_time = st.time_input("To time", value=dt.time(17, 0), step=900, key="provision_to_time")

        submitted = st.form_submit_button("Provision Access", use_container_width=True)

    if not submitted:
        return

    upn_clean = normalize_email(upn)
    from_dt = combine_date_time(from_date, from_time)
    to_dt = combine_date_time(to_date, to_time)

    if not is_valid_email(upn_clean):
        st.error("Enter a valid user email.")
        return

    if not selected_groups:
        st.error("Select at least one group.")
        return

    window_error = validate_window(from_dt, to_dt)
    if window_error:
        st.error(window_error)
        return

    try:
        overlaps = find_overlaps(session, upn_clean, selected_groups, from_dt, to_dt)
        if not overlaps.empty:
            st.warning("Overlapping access already exists.")
            display_access_table(overlaps)
            return

        insert_access_rows(session, upn_clean, selected_groups, from_dt, to_dt, current_user_email)
        st.success(f"Provisioned {len(selected_groups)} group{'s' if len(selected_groups) != 1 else ''} for {upn_clean}.")
    except Exception as exc:
        st.error(f"Failed to provision access: {exc}")


def render_manage_tab(session: Session, current_user_email: str) -> None:
    st.markdown('<div class="section-label">Find Access</div>', unsafe_allow_html=True)

    search_email = st.text_input("User email", key="manage_search_email", placeholder="name@coles.com")

    if not search_email.strip():
        st.markdown('<span class="small-muted">Enter an email address to manage access.</span>', unsafe_allow_html=True)
        return

    try:
        df = get_access_records(session, search_email=search_email, active_only=False, limit=500)
    except Exception as exc:
        st.error(f"Failed to load access: {exc}")
        return

    if df.empty:
        st.info("No access found.")
        return

    st.markdown('<div class="section-label">Records</div>', unsafe_allow_html=True)
    display_access_table(df)

    labels = [build_row_label(row) for _, row in df.iterrows()]
    selected_idx = st.selectbox(
        "Select record",
        options=list(range(len(df))),
        format_func=lambda i: labels[i],
        key="manage_selected_record",
    )

    row = df.iloc[selected_idx]

    st.markdown('<div class="section-label">Edit Window</div>', unsafe_allow_html=True)

    current_from = safe_to_datetime(row["From Date"]) or dt.datetime.now()
    current_to = safe_to_datetime(row["To Date"]) or (dt.datetime.now() + dt.timedelta(days=30))
    record_suffix = re.sub(r"[^A-Za-z0-9_]", "_", f"{row['Email']}_{row['Group']}_{row['Created Key']}")[:100]

    with st.form(f"manage_update_form_{record_suffix}", clear_on_submit=False):
        d1, t1, d2, t2 = st.columns(4)

        with d1:
            from_date = st.date_input("From date", value=current_from.date(), key=f"manage_from_date_{record_suffix}")
        with t1:
            from_time = st.time_input(
                "From time",
                value=current_from.time().replace(microsecond=0),
                step=900,
                key=f"manage_from_time_{record_suffix}",
            )
        with d2:
            to_date = st.date_input("To date", value=current_to.date(), key=f"manage_to_date_{record_suffix}")
        with t2:
            to_time = st.time_input(
                "To time",
                value=current_to.time().replace(microsecond=0),
                step=900,
                key=f"manage_to_time_{record_suffix}",
            )

        update_clicked = st.form_submit_button("Update Access Window", use_container_width=True)

    if update_clicked:
        from_dt = combine_date_time(from_date, from_time)
        to_dt = combine_date_time(to_date, to_time)

        window_error = validate_window(from_dt, to_dt)
        if window_error:
            st.error(window_error)
            return

        try:
            overlaps = find_overlaps(
                session=session,
                upn=row["Email"],
                groups=[row["Group"]],
                from_dt=from_dt,
                to_dt=to_dt,
                exclude_email=row["Email"],
                exclude_group=row["Group"],
                exclude_created_key=row["Created Key"],
            )

            if not overlaps.empty:
                st.warning("Updated window overlaps with another row.")
                display_access_table(overlaps)
                return

            rows_updated = update_access_window(session, row, from_dt, to_dt, current_user_email)
            if rows_updated == 0:
                st.warning("No row was updated. Refresh and try again.")
            else:
                st.success("Access window updated.")
                st.rerun()
        except Exception as exc:
            st.error(f"Failed to update access: {exc}")

    st.markdown('<div class="section-label">Remove Access</div>', unsafe_allow_html=True)

    selected_key = f"{row['Email']}|{row['Group']}|{row['Created Key']}"
    confirm_key = "confirm_remove_access_key"

    if st.session_state.get(confirm_key) != selected_key:
        if st.button("Remove Access", use_container_width=True, key="remove_access_first"):
            st.session_state[confirm_key] = selected_key
            st.rerun()
    else:
        c1, c2 = st.columns(2)

        with c1:
            if st.button("Confirm Remove Access", use_container_width=True, key="remove_access_confirm"):
                try:
                    rows_updated = expire_access_row(session, row, current_user_email)
                    st.session_state[confirm_key] = None

                    if rows_updated == 0:
                        st.warning("No active or scheduled access was removed.")
                    else:
                        st.success("Access removed.")

                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed to remove access: {exc}")

        with c2:
            if st.button("Cancel", use_container_width=True, key="remove_access_cancel"):
                st.session_state[confirm_key] = None
                st.rerun()


def main() -> None:
    apply_theme()

    try:
        session = get_session()
    except Exception as exc:
        st.error(f"Unable to connect to Snowflake: {exc}")
        st.stop()

    current_user_email = get_current_user_email(session)
    render_header(current_user_email)

    view_tab, provision_tab, manage_tab = st.tabs(["View", "Provision", "Manage"])

    with view_tab:
        render_view_tab(session)

    with provision_tab:
        render_provision_tab(session, current_user_email)

    with manage_tab:
        render_manage_tab(session, current_user_email)


if __name__ == "__main__":
    main()
