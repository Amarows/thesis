# Research Plan: Influence of External Information Shocks on Equity Portfolio Manager Decision-Making

## Titles

> Reducing Emotional Bias in Investment Portfolio Management.

Other titles I do not like because they are either too complex or too vague:
- Decision Support Systems for Reducing Emotional Biases in Equity Portfolio Management
- Influence of External Valuation Shocks on Equity Portfolio Manager Decision-Making
- Equity Portfolio Manager Decision-Making in Response to External Information Events
- Behavioral Biases in Equity Managers’ Responses to External Information Shocks
- AI-Assisted Decision Support for Equity Managers Facing External Market Shocks
- Mitigating Behavioral Overreactions in Equity Manager Decisions During External Information Shocks
- Digital Intervention into Decision Making for Equity Managers Facing External Market Shocks

---

## Research Question

Does a decision-support system reduce emotional biases and improve the consistency and quality of portfolio managers’ investment decisions in response to emotionally charged public information?

---

## Hypotheses

### Hypothesis Set (Short)

> H₁: Do news-driven emotions influence investment decisions?  
> H₂: Does support improve decision outcomes?  
> H₃: Does support reduce decision inconsistency?

### Full Hypothesis Set

- **H1 – Influence of Information Shocks on Decisions**
  - Tested using survey responses collected without displaying the Shock Score, examining how different shocks lead to different managerial decisions.
  - **H1₀**: External financial information shocks have no statistically significant effect on managerial investment decisions 
  - measured by the risk-return ratio of the portfolio. 
  - **H1ₐ**: External financial information shocks have statistically significant effect on managerial investment decisions 
  - measured by the risk-return ratio of the portfolio.
  
- **H2 – Value Added of the Shock Score (the main one)**
  - Tested through portfolio simulations comparing manager-only strategies with Shock Score–supported strategies.
  - **H2₀**: Introducing Shock Score for investment decision-making have no 
  - statistically significant effect on the risk return ratio of the portfolio.
  - **H2ₐ**: Introducing Shock Score for investment decision-making have 
  - statistically significant effect on the risk return ratio of the portfolio.

**Definition of the Shock Score**: A numerical indicator derived from news headlines using sentiment and event-type classification, designed to quantify the emotional and informational intensity of external news and events. The Score enables managers to reduce behavioral overreaction.

- **H₃ (last chapter extension) – Behavioral Impact of the Shock Score (Optional -- do not turn this into a hypothesis, let's try to convert this into practical recommendation)**
  - Tested by comparing survey responses before and after displaying the Shock Score for the same events.
  - **H₀₃**: The Shock Score does not change the consistency or dispersion of managerial responses to financial information shocks.
  - **Hₐ₃**: The Shock Score changes the consistency or reduces the dispersion of managerial responses to financial information shocks.
---

## Variable Operationalization Consistency Map (Chapter 2)

| Element | H₁ | H₂ |
|---|---|---|
| **Hypothesis (2.5)** | SC_total → NRS | ShowSC → risk–return ratio |
| **Clarifying paragraph** | Links NRS to Sharpe/Sortino via simulation | Specifies Sharpe/Sortino, within-subject |
| **Research question (2.4)** | Shocks → NRS + downstream portfolio | Shock Score → portfolio outcomes |
| **Objective (2.3)** | Shocks → NRS shifts | Score → decision moderation + outcome changes |
| **Definition IV (2.6.3)** | SC_total = PCA composite | ShowSC = treatment indicator |
| **Definition DV (2.6.4/2.6.5)** | NRS (7-point scale) | Sharpe/Sortino |
| **Tech Appendix regression** | y_i,e (NRS) = α + β₁·SC_total + controls | Outcome_j = α + τ·ShowSC + controls |

---

## Biases

     Affect Heuristic (or Affect Bias)
- This refers to decisions being driven by emotional responses to stimuli (e.g., fear, excitement, media tone) rather than rational evaluation.
- In investment, it causes overreaction to emotionally charged events (e.g., panic-selling after a negative news headline).

Closely related concepts
- Framing bias – when the way information is presented alters the decision. May contribute, but it's secondary.
- Availability bias – when recent or vivid events dominate judgement. Often overlaps, but is more cognitive.
- Loss aversion / regret aversion – affect outcomes but are not the core mechanism in your case.


---

## Literature Review

- Behavioral Biases in Investment Decisions (80% of papers should be within last 10 years)
  - **Tversky & Kahneman (1974)** – Identified key heuristics (e.g. availability, representativeness) that lead to biased decision-making under uncertainty.
  - **Kahneman & Tversky (1979)** – Introduced Prospect Theory, showing how people overweight losses relative to gains.
  - **Shefrin & Statman (1985)** – Described the disposition effect, where investors irrationally sell winners and hold losers.
  - [**De Bondt & Thaler (1985)**](https://www.jstor.org/stable/2327804)– *Key Source*  
    Empirically demonstrated that investors overreact to public information, causing extreme price movements followed by reversals. This landmark study was among the first to show that investor psychology—particularly overreaction to emotionally charged news—leads to predictable return anomalies. It directly supports the thesis argument that emotionally influenced decisions deviate from rational valuation and should be corrected.
  - **Barberis & Thaler (2003)** – Reviewed the main behavioral finance biases and their effects on investor and market behavior.
  - Shefrin, H., & Statman, M. (1985) – introduce concepts like disposition effect and affective reaction to explain irrational trading.
  - Lo, A. W. (2012) – Adaptive Markets Hypothesis highlights emotion-driven behavior under uncertainty.
  - Da, Z., Engelberg, J., & Gao, P. (2011) – show how media sentiment (measured via news tone) predicts abnormal investor reaction.
  - Shiller, R. J. (2000) – explains market volatility via narrative and emotion, not just fundamentals.

- Managerial Decision-Making Under Uncertainty
  - **Simon (1955)** – Introduced bounded rationality: managers satisfice rather than optimize under complexity.
  - **March & Shapira (1987)** – Showed how managers frame risk relative to targets and survival thresholds.
  - **Kahneman & Lovallo (1993)** – Identified a bias pattern: cautious decision-making paired with over-optimistic forecasts.
  - **Malmendier & Tate (2005)** – Linked CEO overconfidence to systematic overinvestment and misallocation of capital.
  - **Knight (1921)** – Distinguished between measurable risk and unquantifiable uncertainty in economic behavior.

- Tools to Mitigate Emotional Bias
  - **Shefrin (2002)** – Proposed practical techniques to reduce investment bias: pre-commitment, rules-based discipline, diversification.
  - **Thaler & Sunstein (2008)** – Introduced nudging: small interventions in decision architecture to improve behavior without restricting choice.
  - [**Lo (2004)**](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=602222) – *Key Source*  
    Proposed the Adaptive Markets Hypothesis, bridging efficient markets with behavioral finance by suggesting investor behavior evolves with context. Lo’s model supports flexible decision-support systems (DSS) that adapt to changing environments, helping mitigate emotional bias through structured, data-driven guidance.
  - **Statman (2019)** – Shifted behavioral finance from diagnosis to prescription: advisors as behavioral coaches, goal-based planning, and decision framing.
  - [**Kendzia & Lemke (2025)**](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5498599) – Outlined evidence-based debiasing tools: rules-based trading, cognitive training, and digital interventions.

- Market Reactions to Public Information
  - **Fama (1970)** – Defined market efficiency: asset prices reflect all available information instantly and rationally.
  - **Shiller (1981)** – Challenged EMH by showing that price volatility exceeds what fundamentals (like dividends) justify.
  - **Tetlock (2007)** – Found that negative news tone predicts short-term market underperformance and investor reaction.
  - **Baker & Wurgler (2007)** – Created a sentiment index showing how optimism and pessimism distort prices—especially in hard-to-value stocks.
  - **Engelberg & Parsons (2011)** – Proved that mere exposure to news (not necessarily content) drives localized price and volume reactions.

 - Decision-Support Systems in Investment
   - **Markowitz (1952)** – Laid the foundation for quantitative portfolio selection and rational diversification strategies.
   - **D’Acunto et al. (2019)** – Evaluated robo-advisors and found improved outcomes with limitations on personalization.
   - **Krieger & Lausberg (2015)** – Described how DSS frameworks support complex real-estate and investment decisions under uncertainty.
   - **Cardillo & Chiappini (2024)** – Reviewed AI-driven investment tools, showing how technology shapes modern decision support.

---

## Survey Design

An online survey will be conducted using Microsoft Forms, targeting portfolio managers and members of investment management teams.
- Respondents will evaluate a set of real historical news events related to a predefined portfolio of stocks.
- For each company, respondents will be shown one version of a similar information shock (e.g., comparable news type or severity), rather than the same event repeated.
- Events will be randomly assigned so that different respondents receive comparable events with and without the Shock Score, avoiding anchoring or learning effects.
- For each event, respondents will indicate:
    - Recommended action
    - Perceived severity
    - Expected impact horizon
    - Confidence level
- Responses to events without the Shock Score will be used to test whether information shocks influence managerial decisions (**H₁**).
- Responses to comparable events with versus without the Shock Score will be used to assess the behavioral impact of the decision-support system (**H₃**).
- The survey is intentionally concise to encourage participation while enabling robust statistical analysis.

## Short Research Plan

1. **Portfolio selection**: 15 stocks subject to test.
2. **Data collection**: Collect historical daily data.
3. **Shock calculation**: Collect news with shocks -> use AI (ChatGPT) to extract sentiment -> calculate score.
4. **Manager assessment**: Collect manager assessment of the same news via Microsoft Forms.
5. **Validation**: Compare managerial decisions with mutual fund portfolio dynamics (are decisions really reflected in portfolio compositions?).
6. **Simulation**: Compare decisions with score by simulating 3 portfolios:
    - **With manager reactions**: CAPM, conventional portfolio; investigate if behavioral finance can provide correction tools.
    - **With manager reactions and score**.
    - **With score correction only**.
7. **Conclusion**: Determine if the score statistically improves decision making.

## Full Research Plan

1. **Construct test object**
    - Construct a 15-stock portfolio (fixed universe; daily frequency).
    - Collect historical daily prices for stocks and a benchmark (e.g., sector ETF + broad index) for risk adjustment.
2. **Shock event dataset (primary data)**
    - Build a database of news events linked to the 15 stocks (headline, timestamp, source, type).
    - Use ChatGPT-assisted NLP to extract sentiment, event type, and optionally "urgency".
    - Combine these into a **Shock Score**.
3. **Manager assessment dataset (primary data)**
    - Use Microsoft Forms to collect manager assessments (severity, direction, horizon, action, confidence).
    - Target: portfolio managers / investment team members (aim ≥ 50 responses).
4. **"Do decisions show up in real portfolios?"**
    - Use mutual fund or strategy proxy to test if composition changes align with manager assessments or the Shock Score.
    - Note: Holdings frequency (quarterly) makes this a medium-term validation.
5. **Portfolio simulations (three strategies)**
    - **Manager-only decisions**: Rebalancing driven by survey decisions (aggregated rule).
    - **Manager + Shock Score support**: Decisions informed by managers but adjusted/filtered by the score.
    - **Shock Score only**: Rule-based score strategy (baseline automation).
6. **Conclusion**
    - Test if the Shock Score improves risk-adjusted performance/drawdown and/or reduces decision noise.

## Problems & Nuances

- **Data Latency**: Mutual fund holdings are often quarterly/monthly; use for medium-term validation, not immediate reaction. Use price/volatility event windows for short-term.
- **Unit of Analysis**: Use event-level observations (score features, manager response, realized outcome).
- **Measurable Quality**: Operationalize as abnormal volatility capture, reduction in adverse moves, and risk-adjusted metrics.
- **Behavioral Correction**: Use practical framing like thresholding, confirmation delay, asymmetric response rules, and attention filters.

## Instruments

- **Benzinga (BZ)** – Real-time market and equity news covering earnings, sector trends, and macroeconomic developments. Well suited for identifying short-horizon market-moving events.
- **Dow Jones Real-Time News (DJ-RT)** – Institutional news feed with high editorial standards, covering corporate disclosures, macroeconomic data, and global financial markets.
- **Fly on the Wall (FLY)** – Event-driven market intelligence focused on analyst actions, earnings reactions, and short-term trading catalysts.

## Other

### The Question
“How can portfolio manager react to sudden information shocks without falling into cognitive traps?”

### Pitch
Managers across industries face unexpected information shocks that often trigger fast decisions under pressure. These reactions are frequently shaped by behavioral biases. My thesis aims to design and test a decision-support system that helps managers evaluate such shocks in a more structured, bias-aware, and evidence-based way.

### Scope (Financial Portfolio Focus)
1. Construct financial portfolio as an experimental object.
2. Collect primary data (external events & manager reactions).
3. Develop a **Shock Impact Score**.
4. Test the system empirically via performance comparison.
5. Demonstrate mitigation of behavioral overreaction.
6. Generalize the framework for other managerial contexts.

### Framework
`External Shocks -> Text Processing -> Severity and Sentiment -> Shock Score -> Decision Correction -> Short Term Performance Indicators`

### Why It Matters
Combines behavioral economics, decision science, and AI into a practical tool.
- **Managerial Value**: Reduces biases, filters noise, supports decisions under uncertainty.
- **Methodological Value**: Novel SIS score, AI-based filtering, structured news data.
- **Strategic Value**: Enhances risk management and digital transformation.
- **Academic Value**: Bridges multiple fields, scalable to other domains.

## List of Crazy Ideas
- **Core Thesis**: SIS score, shock data as primary data, AI/LLM for classification, focus on overreaction.
- **Extensions**: Scenario analysis, SIS-based hedging rules, LLM fine-tuning, event clustering, human vs. AI consistency.
- **Strategic**: Frame as generalizable beyond finance, align with SDGs (8, 9, 16).

## Tools, Data Sources, and Methods

| Category | Details / Notes |
| :--- | :--- |
| **News & Event Data Sources** | Yahoo Finance, Reuters, BusinessWire, SEC/EDGAR, company press releases, X/Twitter. |
| **Interactive Brokers API** | Use for market data (prices, returns, volatility around events). Not ideal for news extraction. |
| **Python Tools** | pandas, numpy, matplotlib, scikit-learn, NLTK, spaCy, transformers. |
| **AI / Model Training** | Fine-tune or prompt AI models for event classification and shock scores. |
| **Statistical Methods** | Event studies, sentiment scoring, correlation tests, regression models, scenario comparison. |
| **DSS Components** | Shock Impact Score (SIS), metrics, AI classification, rule-based guidance. |

## SBS Thesis Topic Suitability Table
| # | Criterion | Suitability Notes |
| :--- | :--- | :--- |
| 1 | Relevance to Business Administration | Focuses on managerial decision-making, behavioral biases, and risk governance. |
| 2 | Importance and Interest | Addresses real-world challenges of reacting to shocks under pressure. |
| 3 | Manageability | Well-defined scope, executable within 20,000 words. |
| 4 | Availability of Resources | Uses accessible primary data (news) and secondary literature. |
| 5 | Primary Research Requirement | Satisfied via manual collection/classification of shocks. |
| 6 | Clear Hypotheses | Connects shocks to outcomes via causal structure. |
| 7 | Quantitative Analysis Feasibility | Event studies and regression are within EMBA expectations. |
| 8 | Backtesting and Validation | Two-layer test ensures robustness and managerial relevance. |
| 9 | Strong Literature Base | Solid foundation in behavioral economics and decision science. |
| 10 | Ethical & SDG Alignment | Aligns with SDG 8, 9, 16; addresses AI transparency. |
| 11 | Not Overly Technical | AI is framed as a support tool, not an engineering model. |
| 12 | Mentor Fit | Aligns with mentor's expertise in risk and managerial judgement. |
| 13 | Originality | Novel combination of shock scoring, bias mitigation, and AI. |
