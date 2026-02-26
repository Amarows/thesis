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

1. Recognition without dominance. Companies should be familiar enough to a generalist equity portfolio manager that no research effort is required to understand the business model, but not so prominent that strong prior beliefs or emotional associations dominate the response. Operationally, this means excluding the top 20 constituents by market capitalisation (e.g., Apple, Microsoft, Amazon, NVIDIA) while retaining names that any active equity PM would recognise. The objective is ecological validity -- professional managers make decisions about real companies, not fictitious entities -- while constraining the familiarity bias that arises when managers hold strong personal views about a specific stock (Weber, Siebenmorgen, and Weber, 2005).

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

### 2.2 Shock Identification Algorithm

Candidate event days are identified through a two-stage screening process.

Stage 1 -- Statistical screening. For each stock in the universe, compute the rolling 60-trading-day historical volatility (standard deviation of daily log returns). Flag days where the absolute daily return exceeds 2.0 standard deviations from the stock's trailing mean return. This threshold identifies days with statistically unusual price movements relative to the stock's own history.

Additionally, compute the relative abnormal return -- the stock's daily return minus the broad market return (S&P 500) on the same day. This step distinguishes firm-specific shocks from market-wide movements. A day on which the entire market declines 3% represents a systematic shock, not a firm-specific information event. For scenario selection, candidate days must exhibit a relative abnormal return exceeding 1.5 standard deviations of the stock's historical relative return distribution.

Stage 2 -- News attribution. For each candidate event day surviving Stage 1, verify that the Benzinga news feed via the Interactive Brokers API contains at least one identifiable, firm-specific news item for that stock on the event day or the prior trading session's close. The news item must be attributable to a specific corporate or market event (earnings surprise, regulatory action, management change, legal proceeding, product announcement, etc.) rather than to generic market commentary, sector rotation notes, or analyst opinion pieces without new information content.

This two-stage process produces a pool of candidate stock-day-news triples from which the final twelve scenarios are selected.


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

Market regime balance: each block draws events from at least two distinct market regimes.

Sector non-repetition: within each block, no two scenarios feature stocks from the same GICS sector, unless the pool makes this infeasible, in which case no sector appears more than twice within a single block.

#### 2.3.3 Manager-to-Block Assignment

Each respondent is randomly assigned to one block upon survey entry. With a target sample of approximately 100 managers, each block receives approximately 33 respondents. Within each block, the Latin square counterbalanced design described in section 4.2.3 of the thesis operates independently: it rotates treatment assignment (which 6 of the 12 scenarios receive ShowSC = 1) and presentation order across respondents within the block.

Block assignment is recorded as a categorical variable (BlockID) and included as a fixed effect in the pooled regression specifications to absorb any between-block heterogeneity.


### 2.4 Selection Summary Table

### 2.4 Selection Summary Tables

The following tables are populated during scenario construction and reported in Chapter 4 as documentation of the selection process. One table is produced per block.

Table 2.4a: Block A Scenario Selection Summary

| Scenario | Stock | GICS Sector | Event Date | Event Type | Shock Direction | SC_total | Relative Abnormal Return | Market Regime |
|---|---|---|---|---|---|---|---|---|
| A1 | | | | | | | | |
| ... | | | | | | | | |
| A12 | | | | | | | | |

Table 2.4b: Block B Scenario Selection Summary

[Same structure as Table 2.4a, scenarios B1 through B12]

Table 2.4c: Block C Scenario Selection Summary

[Same structure as Table 2.4a, scenarios C1 through C12]


## References Cited in This Protocol

- DeMiguel, V., Garlappi, L., and Uppal, R. (2009). Optimal versus naive diversification: How inefficient is the 1/N portfolio strategy? Review of Financial Studies, 22(5), 1915-1953.
- Li, X., Shah, S., Noyan, R., and Gao, Z. (2016). Stock prediction based on news sentiment analysis. IEEE Engineering Management Review.
- Tversky, A., and Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. Science, 185(4157), 1124-1131.
- Weber, E. U., Siebenmorgen, N., and Weber, M. (2005). Communicating asset risk: How name recognition and the format of historic volatility information affect risk perception and investment decisions. Risk Analysis, 25(3), 597-609.