# Scenario Selection Protocol

## Purpose

This document specifies the criteria, procedures, and rationale for constructing the thirty-six information shock scenarios used in the primary data collection instrument (Chapter 4). The scenarios are organised into three mutually exclusive blocks of twelve, with each block administered to a randomly assigned subset of approximately 33 respondents. The multi-block design extends event coverage and strengthens external validity while preserving within-block experimental control.

---

## 1. Portfolio Design and Stock Selection

### 1.1 Stock Universe Size

The study requires exactly 36 unique stocks to populate the thirty-six scenario slots across three blocks. Each stock contributes exactly one scenario (one stock-day-news triple) and appears in exactly one block. No stock appears in more than one scenario or more than one block. This mutual exclusivity by stock ensures that blocks are fully independent mini-experiments: no manager encounters the same company as any manager in a different block, eliminating cross-block stimulus dependence and enabling clean between-block comparisons.

The portfolio is constructed with a target of 39 candidate stocks. The 36 best candidates -- those with qualifying triples that jointly satisfy the balance constraints described in section 2.3 -- are assigned to blocks. The remaining candidates serve as buffer for pilot-testing attrition or quality failures.

### 1.2 Company Selection Criteria

Stocks are drawn from the S&P 500 index, selecting mid-to-large capitalisation constituents that satisfy three conditions:

1. Recognition without dominance. Companies should be familiar enough to a generalist equity portfolio manager that no research effort is required to understand the business model, but not so prominent that strong prior beliefs or emotional associations dominate the response. Operationally, this means excluding the top 10 constituents by market capitalisation (e.g., Apple, Microsoft, Amazon, NVIDIA) while retaining names that any active equity PM would recognise. The objective is ecological validity -- professional managers make decisions about real companies, not fictitious entities -- while constraining the familiarity bias that arises when managers hold strong personal views about a specific stock (Weber, Siebenmorgen, and Weber, 2005).

2. Adequate news coverage. Each stock must have sufficient Benzinga news flow via the Interactive Brokers API during the event selection window (section 2) to permit Shock Score computation. Stocks with fewer than one news article per week on average are excluded, consistent with the filtering approach used in prior sentiment-based trading strategy research (Li, Shah, Noyan, and Gao, 2016).

3. Active trading and liquidity. Each stock must have average daily trading volume sufficient to make portfolio adjustment decisions plausible. Illiquid or thinly traded names would undermine the ecological validity of the scenario, as professional PMs would not hold such positions in a diversified equity portfolio.

Company names are not masked. Masking names would eliminate familiarity bias but at a disproportionate cost to ecological validity -- portfolio managers do not evaluate abstract entities, and the realism of the decision context is central to eliciting meaningful NRS responses. Instead, scenario instructions explicitly direct the manager to assume the stock is held in the portfolio and to respond based on the information presented, not on personal views of the company. Residual familiarity effects are acknowledged as a limitation (section 2.8.2 of the thesis).

### 1.3 Sector Diversification

Stocks are sampled from at least 8-10 distinct GICS (Global Industry Classification Standard) sectors. Sector concentration would introduce a confound: managers specialising in the over-represented sector would respond from a systematically different knowledge base than generalists, creating uncontrolled heterogeneity in expertise across respondents. Diversification across sectors also makes the portfolio construction more plausible -- a portfolio concentrated in two sectors would not credibly represent a diversified equity book.

The target sector allocation is approximately proportional to S&P 500 sector weights, with the constraint that no single sector contributes more than 5 of the 36 stocks and no sector contributes fewer than 1. Within each block of 12, the sector non-repetition constraint described in section 2.3 applies independently.

### 1.4 Portfolio Weighting

The portfolio uses equal (1/N) weighting across all constituent stocks. This decision is motivated by three considerations:

First, transparency. Equal weighting is immediately interpretable by respondents and requires no auxiliary assumptions. The manager can focus cognitive resources on the shock-response decision rather than on evaluating or questioning the portfolio construction methodology.

Second, neutrality. CAPM-optimised or mean-variance weights would depend on estimated parameters (expected returns, covariance matrices) that are themselves uncertain and potentially contested. Disagreement with the weighting scheme would introduce an uncontrolled confound -- some managers might adjust their NRS response to "correct" for what they perceive as a misallocated portfolio, rather than responding purely to the information shock.

Third, precedent. DeMiguel, Garlappi, and Uppal (2009) demonstrated that the 1/N portfolio performs competitively with optimised strategies in out-of-sample evaluation, and naive diversification is widely used as a benchmark in both experimental and empirical finance research.

The equal-weight assumption is communicated to respondents in the scenario preamble: "You manage a diversified equity portfolio with equal weights across 36 stocks." For the portfolio simulation in the Technical Appendix, the 1/N starting allocation (approximately 2.8% per stock) is the baseline from which NRS-implied adjustments are computed. Each manager's simulation applies NRS-implied adjustments to the 12 stocks in their assigned block and holds the remaining 24 at baseline weight.

---

## 2. Event Selection

### 2.1 Historical Window

Events are drawn from a window of approximately 18-36 months prior to survey administration. This range balances three competing concerns:

- Freshness. Events should be recent enough that the market context (regulatory environment, macroeconomic regime, corporate landscape) remains recognisable and plausible to respondents.
- Recognition avoidance. Events should not be so recent that managers remember the actual outcome and anchor on realised returns rather than responding to the scenario as presented under uncertainty.
- Data availability. The window must contain sufficient candidate events across the required number of stocks and sectors to permit the balanced selection described below.

Events involving companies that have been acquired, delisted, or fundamentally restructured since the event date are excluded, as the scenario context would be confusing or implausible to respondents.

### 2.1A Intraday Data Resolution

All intraday price and volume data are sampled at 30-minute intervals, producing 13 bars per full trading day (09:30 to 16:00 ET). This resolution is selected to balance three considerations. First, temporal attribution: a 30-minute window provides sufficient granularity to isolate the price response to a firm-specific news event from pre-existing intraday trends, reducing the ambiguity that arises when the shock timestamp and the observed price move are separated by up to 60 minutes in hourly data. Second, visual clarity: the 13 bars per day produce a chart that is legible and interpretable within the survey context, whereas 15-minute bars (26 per day) introduce visual noise that does not carry decision-relevant signal for the respondent. Third, signal robustness: Shock Score components -- particularly the abnormal intraday volume ratio (AI_e) and the bar-level return used in severity computation (ES_e) -- require sufficient volume aggregation to produce stable estimates. For lower-liquidity constituents in the portfolio universe (e.g., Utilities and Real Estate names), 30-minute bars maintain adequate volume depth, whereas 15-minute bars risk inflating noise in these components.

The rolling statistics used to calibrate the Shock Score components (historical mean and standard deviation of bar-level returns and volume) are recomputed at the 30-minute frequency over the same trailing 60-trading-day window specified in the statistical screening algorithm. All references to "hourly return" in the Shock Score construction are replaced by "30-minute bar return" at the corresponding interval.

### 2.2 Shock Identification Algorithm

Candidate event days are identified through a three-stage screening process.

Stage 1 -- Statistical screening. For each stock in the universe, compute the rolling 60-trading-day historical volatility (standard deviation of daily log returns). Flag days where the absolute daily return exceeds 2.0 standard deviations from the stock's trailing mean return. This threshold identifies days with statistically unusual price movements relative to the stock's own history.

Additionally, compute the relative abnormal return -- the stock's daily return minus the broad market return (S&P 500) on the same day. This step distinguishes firm-specific shocks from market-wide movements. A day on which the entire market declines 3% represents a systematic shock, not a firm-specific information event. For scenario selection, candidate days must exhibit a relative abnormal return exceeding 1.5 standard deviations of the stock's historical relative return distribution.

Stage 1B -- Within-day causal plausibility screen. Candidate event days that pass the daily-level statistical screen (Stage 1) are subjected to an additional within-day filter to ensure that the observed price move is temporally attributable to the identified shock bar rather than to a pre-existing intraday trend.

For each candidate day, compute the absolute return for each 30-minute bar over the trading session. Define the shock bar return as the absolute return of the bar to which the news article is assigned (per the intraday shock assignment rule in Stage 2). Define the reference return as the median absolute 30-minute bar return for all non-shock bars on the same day.

The candidate passes the within-day screen if the shock bar return exceeds 1.5 times the reference return. This multiplier ensures that the shock bar exhibits a price move that is meaningfully larger than the typical intraday fluctuation for that stock on that day, providing visual and statistical evidence that the news event is associated with a distinct price response.

Candidate days that pass the daily-level screen (Stage 1) but fail the within-day causal plausibility screen (Stage 1B) are excluded from the candidate pool. The rationale is that a scenario in which the stock declines (or advances) steadily throughout the day, with no discernible acceleration at the shock timestamp, would present an ambiguous visual narrative to survey respondents. The participant would be unable to distinguish the shock-driven move from the pre-existing trend, weakening the ecological validity of the scenario and potentially introducing noise into the NRS response.

The 1.5x multiplier is calibrated to retain approximately 60 to 70 percent of daily-level candidates. If this threshold produces a pool that is too small to satisfy the balance constraints in section 2.3, the multiplier may be relaxed to 1.25x and the adjustment documented.

Stage 2 -- News attribution. For each candidate event day surviving Stage 1 and Stage 1B, verify that the Benzinga news feed via the Interactive Brokers API contains at least one identifiable, firm-specific news item for that stock on the event day or the prior trading session's close. The news item must be attributable to a specific corporate or market event (earnings surprise, regulatory action, management change, legal proceeding, product announcement, etc.) rather than to generic market commentary, sector rotation notes, or analyst opinion pieces without new information content.

Intraday shock assignment. Each candidate news article carries a publication timestamp from the Benzinga feed. The shock is assigned to the 30-minute bar whose interval contains the article timestamp. Formally, if the article is published at time t, the shock bar is the interval [b, b + 30 min) such that b <= t < b + 30 min, where b is a bar boundary on the half-hour grid (09:30, 10:00, 10:30, ..., 15:30). For articles published outside regular trading hours (before 09:30 or after 16:00 ET), the shock is assigned to the first bar of the next trading session (09:30 to 10:00) if the article appears after the prior close, or to the last bar of the prior session (15:30 to 16:00) if it appears before the current open. When multiple articles for the same stock fall within the same 30-minute bar, they are treated as a single shock event; article count (AC_e) records the number of distinct articles within that bar.

This three-stage process produces a pool of candidate stock-day-news triples from which the final twelve scenarios are selected.


> ### 2.3 Multi-Block Balanced Scenario Selection

From the candidate pool, thirty-six scenarios are selected and partitioned into three mutually exclusive blocks of twelve (Block A, Block B, Block C). Each block is constructed to satisfy the balance constraints below independently, ensuring that every block constitutes a well-designed experiment in its own right.

#### 2.3.1 Stock-to-Block Assignment

Each of the 36 portfolio stocks is assigned to exactly one block. No stock appears in more than one block. This mutual exclusivity eliminates cross-block stimulus dependence: blocks are fully independent, enabling between-block replication analysis and ensuring that the portfolio simulation for each block operates on a distinct set of holdings.

The assignment algorithm proceeds as follows:

1. For each stock, identify the single best qualifying triple from the candidate pool (highest-quality news attribution, clearest event narrative, SC_total value most useful for satisfying the intensity distribution).
2. Partition the 36 stock-triple pairs into three blocks of 12 using constrained optimisation subject to the balance constraints below.
3. Verify that each block independently satisfies all constraints. If not, swap stock-triple pairs between blocks and re-verify.

#### 2.3.2 Within-Block Balance Constraints

Each block of 12 scenarios must independently satisfy the following:

Shock intensity variation: pre-compute SC_total for each scenario. Each block contains approximately 4 low-intensity events (below the 33rd percentile of the full 36-scenario distribution), 4 medium-intensity events (33rd to 67th percentile), and 4 high-intensity events (above the 67th percentile). Sufficient variation in the independent variable within each block is essential for the within-block H1 regression to have adequate statistical power.

Shock directionality: each block includes both negative and positive shocks in approximately equal proportions (6 negative and 6 positive, or 5 and 7). No block should contain fewer than 4 events of either direction.

Event type diversity: each block includes at least 3 to 4 distinct event types from the classification taxonomy (earnings surprises, regulatory or legal actions, management changes, product or operational news, macro-related firm-specific events).

Article count preference. Scenarios with a single attributable news article in the shock bar (AC_e = 1) are preferred, as they present the respondent with an unambiguous information signal. Scenarios with AC_e = 2 are acceptable if both articles pertain to the same underlying event (e.g., two outlets covering the same earnings release or the same analyst action) and their FinBERT sentiment scores share the same sign. Scenarios with AC_e >= 3 are included only if no single-article or dual-article alternative exists for the corresponding cell in the balance matrix (i.e., for the required combination of intensity, direction, event type, and sector).

When a scenario contains multiple articles (AC_e > 1), the survey instrument presents only the headline with the highest absolute FinBERT sentiment score as the primary headline. The remaining headlines are not displayed to the respondent. The Shock Score components (SC_total and its constituents) continue to be computed using all articles within the shock bar, preserving the composite signal integrity while simplifying the information set that the respondent must process. This decision is documented in the scenario metadata table (Table 4.X) by recording both the total AC_e and the displayed headline for each scenario.

Opening-bar constraint. Shocks assigned to the first 30-minute bar of the trading session (09:30 to 10:00 ET) are subject to an additional screening requirement. Because many stocks exhibit large opening moves driven by overnight information, pre-market order flow, and opening auction mechanics, a shock in the first bar is visually difficult to distinguish from a continuation of the overnight gap. For a first-bar shock to be included, the absolute return of the 09:30 to 10:00 bar must exceed 2.0 times the median absolute 30-minute bar return for all subsequent bars on the same day (a stricter threshold than the 1.5x applied to non-opening bars in Stage 1B). This elevated threshold ensures that the shock bar exhibits a price response that is clearly distinguishable from the mechanical volatility of the opening period.

As a soft constraint on within-block balance, no more than one-third of the scenarios in any single block should have their shock in the first bar (09:30 to 10:00). This limit prevents respondents from forming a pattern expectation that shocks cluster at the open, which could introduce demand characteristics. When the candidate pool permits, shocks occurring from 10:00 ET onward are preferred.

Market regime balance: each block draws events from at least two distinct market regimes.

Sector non-repetition: within each block, no two scenarios feature stocks from the same GICS sector, unless the pool makes this infeasible, in which case no sector appears more than twice within a single block.

#### 2.3.3 Manager-to-Block Assignment

Each respondent is randomly assigned to one block upon survey entry. With a target sample of approximately 100 managers, each block receives approximately 33 respondents. Within each block, the Latin square counterbalanced design described in section 4.2.3 of the thesis operates independently: it rotates treatment assignment (which 6 of the 12 scenarios receive ShowSC = 1) and presentation order across respondents within the block.

Block assignment is recorded as a categorical variable (BlockID) and included as a fixed effect in the pooled regression specifications to absorb any between-block heterogeneity.


### 2.4 Selection Summary Table

The following tables are populated during scenario construction and reported in Chapter 4 as documentation of the selection process. One table is produced per block.

Column definitions:

- **Shock Time (ET):** the 30-minute bar to which the shock is assigned (e.g., "10:00" denotes the 10:00 to 10:30 bar).
- **AC_e:** number of distinct Benzinga articles within the shock bar.
- **Displayed Headline:** the headline presented to survey respondents (the single headline with the highest absolute FinBERT sentiment score when AC_e > 1).
- **Shock Bar / Median Bar Ratio:** the ratio of the absolute shock bar return to the median absolute 30-minute bar return on the same day. Values above 1.5 (or 2.0 for the opening bar) satisfy the within-day causal plausibility screen.

Table 2.4a: Block A Scenario Selection Summary

| Scenario | Stock | Ticker | GICS Sector | Event Date | Shock Time (ET) | Event Type | Direction | SC_total | AC_e | Displayed Headline | Rel. Abnormal Return | Shock Bar / Median Bar Ratio | Market Regime |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | | | | | | | | | | | | | |
| ... | | | | | | | | | | | | | |
| A12 | | | | | | | | | | | | | |

Table 2.4b: Block B Scenario Selection Summary

[Same structure as Table 2.4a, scenarios B1 through B12]

Table 2.4c: Block C Scenario Selection Summary

[Same structure as Table 2.4a, scenarios C1 through C12]


## References Cited in This Protocol

- DeMiguel, V., Garlappi, L., and Uppal, R. (2009). Optimal versus naive diversification: How inefficient is the 1/N portfolio strategy? Review of Financial Studies, 22(5), 1915-1953.
- Li, X., Shah, S., Noyan, R., and Gao, Z. (2016). Stock prediction based on news sentiment analysis. IEEE Engineering Management Review.
- Tversky, A., and Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. Science, 185(4157), 1124-1131.
- Weber, E. U., Siebenmorgen, N., and Weber, M. (2005). Communicating asset risk: How name recognition and the format of historic volatility information affect risk perception and investment decisions. Risk Analysis, 25(3), 597-609.