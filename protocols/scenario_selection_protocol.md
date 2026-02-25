# Scenario Selection Protocol

## Purpose

This document specifies the criteria, procedures, and rationale for constructing the twelve information shock scenarios used in the primary data collection instrument (Chapter 4). The protocol covers three domains: portfolio design and stock selection, event identification and selection, and scenario presentation format. Each decision is grounded in the experimental design requirements established in Chapter 2 and informed by considerations of internal validity, ecological validity, and respondent experience.

---

## 1. Portfolio Design and Stock Selection

### 1.1 Stock Universe Size

The study requires a minimum of 24 unique stocks to populate the twelve scenario-portfolio pairs. Each scenario features a distinct stock-shock combination; no stock appears in more than one scenario. Reusing stocks across scenarios would introduce a within-stock learning confound -- the manager's NRS response to a later scenario featuring the same company would be contaminated by their earlier decision about that company, violating the independence assumption across scenario-level observations.

A target of 24-30 stocks provides a buffer for scenario construction: some candidate events may be discarded during pilot testing or quality screening, and the surplus allows substitution without redesigning the selection pipeline.

### 1.2 Company Selection Criteria

Stocks are drawn from the S&P 500 index, selecting mid-to-large capitalisation constituents that satisfy three conditions:

1. Recognition without dominance. Companies should be familiar enough to a generalist equity portfolio manager that no research effort is required to understand the business model, but not so prominent that strong prior beliefs or emotional associations dominate the response. Operationally, this means excluding the top 20 constituents by market capitalisation (e.g., Apple, Microsoft, Amazon, NVIDIA) while retaining names that any active equity PM would recognise. The objective is ecological validity -- professional managers make decisions about real companies, not fictitious entities -- while constraining the familiarity bias that arises when managers hold strong personal views about a specific stock (Weber, Siebenmorgen, and Weber, 2005).

2. Adequate news coverage. Each stock must have sufficient Benzinga news flow via the Interactive Brokers API during the event selection window (section 2) to permit Shock Score computation. Stocks with fewer than one news article per week on average are excluded, consistent with the filtering approach used in prior sentiment-based trading strategy research (Li, Shah, Noyan, and Gao, 2016).

3. Active trading and liquidity. Each stock must have average daily trading volume sufficient to make portfolio adjustment decisions plausible. Illiquid or thinly traded names would undermine the ecological validity of the scenario, as professional PMs would not hold such positions in a diversified equity portfolio.

Company names are not masked. Masking names would eliminate familiarity bias but at a disproportionate cost to ecological validity -- portfolio managers do not evaluate abstract entities, and the realism of the decision context is central to eliciting meaningful NRS responses. Instead, scenario instructions explicitly direct the manager to assume the stock is held in the portfolio and to respond based on the information presented, not on personal views of the company. Residual familiarity effects are acknowledged as a limitation (section 2.8.2 of the thesis).

### 1.3 Sector Diversification

Stocks are sampled from at least 8-10 distinct GICS (Global Industry Classification Standard) sectors. Sector concentration would introduce a confound: managers specialising in the over-represented sector would respond from a systematically different knowledge base than generalists, creating uncontrolled heterogeneity in expertise across respondents. Diversification across sectors also makes the portfolio construction more plausible -- a portfolio concentrated in two sectors would not credibly represent a diversified equity book.

The target sector allocation is approximately proportional to S&P 500 sector weights, with the constraint that no single sector contributes more than 4 of the 24-30 stocks and no sector contributes fewer than 1.

### 1.4 Portfolio Weighting

The portfolio uses equal (1/N) weighting across all constituent stocks. This decision is motivated by three considerations:

First, transparency. Equal weighting is immediately interpretable by respondents and requires no auxiliary assumptions. The manager can focus cognitive resources on the shock-response decision rather than on evaluating or questioning the portfolio construction methodology.

Second, neutrality. CAPM-optimised or mean-variance weights would depend on estimated parameters (expected returns, covariance matrices) that are themselves uncertain and potentially contested. Disagreement with the weighting scheme would introduce an uncontrolled confound -- some managers might adjust their NRS response to "correct" for what they perceive as a misallocated portfolio, rather than responding purely to the information shock.

Third, precedent. DeMiguel, Garlappi, and Uppal (2009) demonstrated that the 1/N portfolio performs competitively with optimised strategies in out-of-sample evaluation, and naive diversification is widely used as a benchmark in both experimental and empirical finance research.

The equal-weight assumption is communicated to respondents in the scenario preamble. For the portfolio simulation in the Technical Appendix, the 1/N starting allocation is the baseline from which NRS-implied adjustments are computed.

---

## 2. Event Selection

### 2.1 Historical Window

Events are drawn from a window of approximately 18-36 months prior to survey administration. This range balances three competing concerns:

- Freshness. Events should be recent enough that the market context (regulatory environment, macroeconomic regime, corporate landscape) remains recognisable and plausible to respondents.
- Recognition avoidance. Events should not be so recent that managers remember the actual outcome and anchor on realised returns rather than responding to the scenario as presented under uncertainty.
- Data availability. The window must contain sufficient candidate events across the required number of stocks and sectors to permit the balanced selection described below.

Events involving companies that have been acquired, delisted, or fundamentally restructured since the event date are excluded, as the scenario context would be confusing or implausible to respondents.

### 2.2 Shock Identification Algorithm

Candidate event days are identified through a two-stage screening process.

Stage 1 -- Statistical screening. For each stock in the universe, compute the rolling 60-trading-day historical volatility (standard deviation of daily log returns). Flag days where the absolute daily return exceeds 2.0 standard deviations from the stock's trailing mean return. This threshold identifies days with statistically unusual price movements relative to the stock's own history.

Additionally, compute the relative abnormal return -- the stock's daily return minus the broad market return (S&P 500) on the same day. This step distinguishes firm-specific shocks from market-wide movements. A day on which the entire market declines 3% represents a systematic shock, not a firm-specific information event. For scenario selection, candidate days must exhibit a relative abnormal return exceeding 1.5 standard deviations of the stock's historical relative return distribution.

Stage 2 -- News attribution. For each candidate event day surviving Stage 1, verify that the Benzinga news feed via the Interactive Brokers API contains at least one identifiable, firm-specific news item for that stock on the event day or the prior trading session's close. The news item must be attributable to a specific corporate or market event (earnings surprise, regulatory action, management change, legal proceeding, product announcement, etc.) rather than to generic market commentary, sector rotation notes, or analyst opinion pieces without new information content.

This two-stage process produces a pool of candidate stock-day-news triples from which the final twelve scenarios are selected.

### 2.3 Balanced Scenario Selection

From the candidate pool, twelve scenarios are selected to satisfy the following balance constraints:

Shock intensity variation. Pre-compute SC_total (the composite Shock Score) for each candidate event using the PCA-based methodology defined in the Technical Appendix to Chapter 2. Select scenarios that span the SC_total distribution: approximately 4 low-intensity events (below the 33rd percentile of the candidate distribution), 4 medium-intensity events (33rd to 67th percentile), and 4 high-intensity events (above the 67th percentile). Sufficient variation in the independent variable is essential for the H1 regression of NRS on SC_total to have adequate statistical power.

Shock directionality. Include both negative and positive shocks in approximately equal proportions -- for example, 6 negative and 6 positive, or 5-5-2 with 2 ambiguous or mixed-signal events. If all scenarios present negative shocks, the study measures only the reduce-exposure side of the NRS scale, and respondents may detect the pattern, introducing demand characteristics that undermine internal validity.

Event type diversity. The twelve scenarios should include at least 4-5 distinct event types from the classification taxonomy used in Shock Score construction (e.g., earnings surprises, regulatory/legal actions, management changes, product/operational news, macro-related firm-specific events). This ensures that SC_total variation reflects genuine differences in shock character rather than differences in article count for a single event type.

Market regime balance. Sample events from at least two distinct market regimes (e.g., a broadly rising market period and a volatile or declining period). Managers' baseline risk appetite is regime-dependent, and drawing all events from a single regime would limit the generalisability of the NRS responses. The prevailing VIX level or trailing 20-day market return on the event date may be recorded as a scenario-level control variable.

Sector non-repetition. No two scenarios should feature stocks from the same GICS sector, unless the stock universe size and candidate pool make this infeasible, in which case no sector should appear more than twice.

### 2.4 Selection Summary Table

The following table is populated during scenario construction and reported in Chapter 4 as documentation of the selection process:

| Scenario | Stock | GICS Sector | Event Date | Event Type | Shock Direction | SC_total | Relative Abnormal Return | Market Regime |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | |
| ... | | | | | | | | |
| 12 | | | | | | | | |

---


## References Cited in This Protocol

- DeMiguel, V., Garlappi, L., and Uppal, R. (2009). Optimal versus naive diversification: How inefficient is the 1/N portfolio strategy? Review of Financial Studies, 22(5), 1915-1953.
- Li, X., Shah, S., Noyan, R., and Gao, Z. (2016). Stock prediction based on news sentiment analysis. IEEE Engineering Management Review.
- Tversky, A., and Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. Science, 185(4157), 1124-1131.
- Weber, E. U., Siebenmorgen, N., and Weber, M. (2005). Communicating asset risk: How name recognition and the format of historic volatility information affect risk perception and investment decisions. Risk Analysis, 25(3), 597-609.