# Scenario Presentation Protocol

### 3.1 Information State and Decision Point

Each scenario places the manager at a decision point shortly after the information shock has occurred but before the full trading day's price resolution. Specifically, the scenario presents:

1. Trailing price context: the stock's daily closing prices for the 20 trading days preceding the event, displayed as a line chart with percentage returns on the y-axis (rebased to 100 at the start of the window).
2. News event: a headline and a 2-3 sentence summary describing the information shock, drawn directly from the Benzinga news feed.
3. Immediate price reaction: the intraday price movement in percentage terms following the news release (e.g., the first 1-2 hours of trading after the event).

The manager is then asked to record their NRS response. The full day's price resolution (close, any bounce-back or continuation) is not shown. This design choice is deliberate: showing the complete outcome would convert the task from a decision under uncertainty into an outcome evaluation, which is not the cognitive process the study aims to measure. The Shock Score's value proposition is precisely at the moment of maximum uncertainty -- when news has hit but the market has not fully digested it.

### 3.2 Price Normalisation

All price information is presented in percentage return terms, with stocks rebased to 100 at the start of the 20-day trailing window. This eliminates the anchoring effect documented by Tversky and Kahneman (1974), whereby identical percentage moves are processed differently depending on absolute price levels (e.g., a 5% decline from $500 to $475 versus from $20 to $19). Percentage framing is also consistent with how professional portfolio managers typically discuss and evaluate positioning -- in basis points and percentage moves rather than dollar changes.

The y-axis of the trailing price chart is labelled as "Indexed Price (Base = 100)" and the immediate reaction is reported as a percentage change (e.g., "-3.2% in the first two hours of trading").

### 3.3 News Presentation

For scenarios with low to moderate SC_total (where the shock is driven by a single or small number of news items), the scenario presents a single representative headline and summary paragraph.

For scenarios with high SC_total (where the shock reflects a cluster of multiple news reports), the scenario presents a brief cluster summary (e.g., "Multiple news sources reported that...") accompanied by the most prominent headline. This approach reflects the genuine information environment associated with high-intensity shocks -- a single headline would understate the attentional intensity that contributes to the elevated SC_total -- while keeping presentation length manageable.

All news text is drawn verbatim or lightly edited for brevity from the Benzinga feed. Editorial commentary, analyst opinions, or forward-looking speculation are excluded; only factual reporting of the event is presented.

### 3.4 Template Consistency

Every scenario follows an identical presentation template to ensure that variation in NRS responses reflects shock content and treatment condition, not presentation format differences. The template consists of:

1. Portfolio context statement (identical across all scenarios): "You manage a diversified equity portfolio with equal weights across [N] stocks. The following event has occurred for one of your holdings."
2. Stock identification: company name, ticker symbol, GICS sector.
3. Trailing price chart (standardised format, percentage returns, 20-day window).
4. News event box: headline in bold, summary paragraph below.
5. Immediate price reaction: percentage move and time window.
6. Treatment condition (ShowSC = 1 only): Shock Score dashboard displaying the four signals -- sentiment direction band, shock severity level, persistence score with horizon bucket, and protocol recommendation.
7. NRS response item: seven-point scale with anchored labels.

The template is implemented in Google Forms with conditional display logic controlling the inclusion or exclusion of the Shock Score dashboard based on the respondent's counterbalancing block assignment.

### 3.5 Number of News Items Per Scenario

The number of news items presented in each scenario is calibrated to SC_total intensity:

- Low SC_total scenarios (1-2 articles in the underlying data): single headline and brief summary.
- Medium SC_total scenarios (3-5 articles): single prominent headline with a summary noting that multiple sources reported the event.
- High SC_total scenarios (6+ articles): cluster summary paragraph with the most prominent headline, explicitly noting the breadth of coverage (e.g., "Covered by 8 major financial news outlets within 2 hours").

This calibration preserves the ecological validity of the information environment -- a high-intensity shock in reality involves a flood of coverage, and presenting a single headline would not convey the attentional pressure that characterises such events.

---

## Summary of Key Design Decisions

| Decision | Choice | Primary Rationale |
|---|---|---|
| Stock universe size | 24-30 unique stocks | No stock reuse across scenarios; buffer for attrition |
| Company names | Real, unmasked (S&P 500 mid-to-large cap) | Ecological validity; familiarity bias managed via instructions |
| Sector coverage | 8-10 GICS sectors minimum | Avoid expertise confound; portfolio plausibility |
| Portfolio weighting | Equal (1/N) | Transparency; neutrality; DeMiguel et al. (2009) precedent |
| Historical window | 18-36 months prior to survey | Balance freshness, recognition avoidance, data availability |
| Shock identification | Two-stage: statistical screen + news attribution | Abnormal return > 2.0 SD + identifiable firm-specific news |
| Shock intensity balance | 4 low, 4 medium, 4 high SC_total | Ensure variation in IV for H1 regression |
| Shock direction | Approximately 6 negative, 6 positive | Utilise full NRS scale; prevent demand characteristics |
| Event type diversity | At least 4-5 distinct event types | SC_total variation reflects shock character, not article count |
| Market regime | Events from at least 2 regimes | Generalisability of NRS responses |
| Decision point timing | After news, before full-day resolution | Measure decision under uncertainty, not outcome evaluation |
| Price presentation | Percentage returns, rebased to 100 | Eliminate absolute-price anchoring (Tversky and Kahneman, 1974) |
| Template format | Standardised across all 12 scenarios | Internal validity: isolate shock content from presentation |
