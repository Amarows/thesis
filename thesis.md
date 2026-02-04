# Front Matter

- Title Page
- Authentication of Work
- Foreword
- Acknowledgements
- Table of Contents
- List of Tables
- List of Figures
- List of Abbreviations and Acronyms
- Executive Summary

# Chapter 1. Introduction

## 1.1 Background of the Problem
### 1.1.1 Emotional Biases in Investment Decision-Making
### 1.1.2 Information Overload and News-Driven Markets
### 1.1.3 Behavioral Reactions to External Financial News

## 1.2 Background of the Study
### 1.2.1 Traditional Portfolio Theory and Rational Decision Assumptions
### 1.2.2 Emergence of Behavioral Finance
### 1.2.3 Decision Support Tools in Modern Portfolio Management

## 1.3 Purpose of the Study
### 1.3.1 Reducing Emotional Overreaction in Portfolio Decisions
### 1.3.2 Role of Quantitative Signals in Managerial Decision Support

## 1.4 Significance of the Study
### 1.4.1 Academic Contribution to Behavioral Finance Literature
### 1.4.2 Practical Relevance for Portfolio Managers
### 1.4.3 Implications for Risk Management Practices

## 1.5 Scope and Delimitations
### 1.5.1 Asset Classes and Market Coverage
### 1.5.2 Time Horizon and Frequency of Decisions
### 1.5.3 Methodological Boundaries of the Study

## 1.6 Structure of the Thesis

-------------------------------
# Chapter 2. Objectives of the Study

## 2.1 Chapter Introduction

## 2.2 Problem Statement
### 2.2.1 Emotional Bias as a Source of Suboptimal Portfolio Decisions
### 2.2.2 Impact of External Information Shocks on Risk–Return Outcomes

## 2.3 Objectives of the Study
### 2.3.1 Assessing the Effect of Information Shocks on Investment Decisions
### 2.3.2 Evaluating the Value Added of the Shock Score
### 2.3.3 Measuring Changes in Portfolio Risk–Return Characteristics

## 2.4 Research Questions
### 2.4.1 Do External Information Shocks Affect Portfolio Risk–Return Ratios?
### 2.4.2 Does the Shock Score Improve Investment Decision Outcomes?

## 2.5 Hypothesis Statement(s)
### 2.5.1 Hypothesis H₁ – Influence of Information Shocks
### 2.5.2 Hypothesis H₂ – Value Added of the Shock Score

## 2.6 Definitions of Key Terms
### 2.6.1 Emotional Bias
### 2.6.2 External Financial Information Shock
### 2.6.3 Shock Score
### 2.6.4 Risk–Return Ratio

## 2.7 Assumptions
### 2.7.1 Availability and Timeliness of Information
### 2.7.2 Consistency of Portfolio Decision Rules

## 2.8 Limitations
### 2.8.1 Measurement of Emotional Intensity
### 2.8.2 Generalizability Across Market Conditions

## 2.9 Chapter Conclusion

-------------------------------
# Chapter 3. Literature Review

## 3.1 Chapter Introduction
### 3.1.1 Purpose and Scope of the Literature Review
### 3.1.2 Positioning of the Study within Existing Research
### 3.1.3 Link Between Literature and Research Hypotheses
The research hypotheses developed in this study rely on several core concepts that are grounded in the behavioral finance and decision-making literature. 
First, the notion of an information shock refers to publicly available news or updates related to individual stocks that generate a material short-term market reaction, 
typically observable at a daily frequency. Such shocks are characterized by their ability to affect short-term price dynamics and volatility without necessarily 
altering the long-term fundamental value or risk–return characteristics of the underlying firm.

Second, the literature reviewed in this chapter suggests that the primary transmission mechanism through which information shocks influence market prices operates via behavioral and emotional biases. Empirical evidence demonstrates that investors and managers frequently overreact to salient or emotionally charged news due to cognitive and affective biases, leading to temporary price distortions rather than rational revaluation based on fundamentals.

Third, the concept of the Shock Score introduced in this thesis is motivated by existing research on sentiment, attention, and volatility-based measures of market reaction. The Shock Score is designed to quantify the emotional intensity of an information shock by capturing abnormal short-term market responses, such as excess daily volatility, that arise from behavioral reactions rather than fundamental reassessment.

Finally, while the literature contains several indices and measures aimed at capturing market sentiment or uncertainty, such as sentiment indices or news-based volatility indicators, there is limited evidence of tools specifically designed to support managerial decision-making at the time of an information shock. This gap motivates the development and empirical testing of the Shock Score as a decision-support mechanism intended to improve investment decisions by reducing behavioral overreaction.

## 3.2 Behavioral Biases in Investment Decision-Making

### 3.2.1 Heuristics and Judgment Under Uncertainty

Professional investors, despite their expertise, are not immune to the cognitive shortcuts and biases that affect human judgment under uncertainty. In fact, several prevalent biases – **overconfidence**, **availability and recency bias**, **herding**, and **emotional/physiological biases** – can cause even expert decision-makers to react in ways that amplify short-term market volatility and lead to overreactions to financial information shocks. Below we discuss each of these biases and their impact on short-term market dynamics.

### Overconfidence

Overconfidence is a well-documented bias wherein individuals exhibit an unwarranted faith in the accuracy of their own information and judgment. In finance, overconfident investors consistently overestimate their ability to predict outcomes and the precision of their private signals ([Barber & Odean, 2001](https://doi.org/10.1162/003355301556400)). This bias manifests even among professionals – for example, successful traders and fund managers can become overconfident in their skill, particularly after a streak of good performance ([Gervais & Odean, 2001](https://doi.org/10.1111/0022-1082.00338)). Overconfidence leads investors to underweight risks and to trade more aggressively than rational benchmarks would predict, often to their own detriment ([Odean, 1999](https://doi.org/10.1093/rfs/12.4.785)). Theoretical models show that overconfident investors introduce **excess volatility** into markets by overreacting to new information: prices can jump more than fundamentals justify due to overly aggressive trading on one’s private views, creating short-run momentum or “drift” that later corrects ([Daniel et al., 1998](https://doi.org/10.1093/rfs/11.4.921)). In essence, overconfidence can cause initial **overreactions** to news (as overconfident traders push prices away from equilibrium) followed by subsequent reversals once reality catches up, thus contributing significantly to short-term market volatility.

### Availability and Recency Bias

Another class of bias arises from the heuristics investors use to judge the importance of information. The **availability heuristic** refers to the tendency to assess the probability or relevance of an event based on how easily examples come to mind ([Tversky & Kahneman, 1974](https://www.science.org/doi/10.1126/science.185.4157.1124)). In practice, this means that **vivid or recent information** often dominates decision-making because it is readily recalled, even if it is not objectively more important. A closely related phenomenon is **recency bias** – the inclination to give disproportionately high weight to the most recent events or data points when forming judgments. Studies have found that decision-makers (including investors) often overweight recent market events relative to earlier information, skewing their expectations ([Hirshleifer, 2020](https://doi.org/10.1146/annurev-financial-012820-025654)). Even seasoned professionals are susceptible: for example, mutual fund managers have been shown to extrapolate their fund’s **recent performance** into their outlook for the overall market, effectively basing forecasts on the very latest returns rather than long-term fundamentals ([Azimi, 2019](https://doi.org/10.1016/j.irfa.2019.101400)). Such availability and recency biases can produce **short-term volatility** by fueling overreactions to the news of the day. When a dramatic new information shock occurs, investors relying on what is most salient in memory may trade on that news en masse, causing prices to **overshoot** (deviating from intrinsic value) before cooler heads prevail. In sum, the dominance of recent, readily-available information in professional judgment can lead to exaggerated market moves in the short run, as initial reactions are not sufficiently tempered by historical perspective.

### Herding

Herding describes the tendency of investors to **mimic the actions of others** instead of relying on their own independent analysis. In uncertain environments, even professional investors often follow the crowd – for instance, by buying or selling a stock simply because many of their peers are doing so – assuming that the collective might know better or as a form of career risk management (it may feel safer to err in a crowd than to err alone) ([Scharfstein & Stein, 1990](https://doi.org/10.1086/261653); [Bikhchandani et al., 1992](https://doi.org/10.1086/261849)). In formal terms, *herd behavior occurs when investors follow or copy others’ investment decisions rather than act on their private information*. This bias is prevalent among institutional money managers and analysts, who sometimes converge on the same trades or forecasts (“crowding” into assets), effectively reducing the diversity of opinions in the market. The herding heuristic can severely amplify short-term market movements. When many investors herd into purchasing an asset, their collective action drives the price **above** what fundamentals warrant (and conversely, herd selling drives prices **below** fair value). Empirical research shows that such herding-induced price pressures tend to be short-lived: assets that are aggressively bought by herds often become **temporarily overvalued**, only to experience negative subsequent returns as prices correct, whereas heavily sold assets bounce back with positive future returns once the overreaction abates ([Dasgupta et al., 2011](https://doi.org/10.1093/rfs/hhq068); [Brown et al., 2014](https://doi.org/10.1016/j.jempfin.2013.09.001)). Notably, herding by professional investors (e.g. mutual fund herding) has been directly linked to destabilizing price dynamics, as synchronized trading by large players pushes the market away from equilibrium in the short run. This further underscores how social or institutional pressures to herd can lead to volatility spikes around information events, as many decision-makers move in lockstep rather than counterbalancing each other.

### Emotional and Physiological Biases

Beyond cognitive heuristics, emotional and physiological factors can heavily influence investors’ judgment under stress. Professional decision-makers are not emotionless robots; feelings such as fear, greed, anxiety, or over-excitement can bias their choices, especially during market shocks. Research in behavioral finance and neurofinance documents that acute **stress and arousal** can impair rational decision-making even in expert traders ([Lo et al., 2005](https://doi.org/10.1016/j.jpsychores.2005.07.002); [Coates & Herbert, 2008](https://doi.org/10.1073/pnas.0704025105)). For instance, during periods of market turmoil or following negative news, **fear** can set in and trigger a stress response that inclines investors to flee from risk. Elevated levels of cortisol (the body’s primary stress hormone) have been shown to correspond with such fearful market conditions. Under high cortisol, traders become more risk-averse and prone to **panic selling**, which can exaggerate a market’s downward movement in a crash. On the flip side, in euphoric market environments, **greed and excitement** can take over. Surges of testosterone (associated with confidence and risk-seeking) have been observed in traders during market rallies; while moderate testosterone can boost optimism and risk appetite, excessive levels can foster reckless overconfidence and **addictive risk-taking** ([Coates et al., 2010](https://doi.org/10.1038/464122a)). This hormonal effect can exacerbate speculative bubbles – traders under its sway keep pushing prices up beyond intrinsic values, expecting the good times to continue unabated. Empirical studies support the impact of emotions on performance: for example, **traders who exhibit extremely intense emotional reactions** to gains or losses (e.g. palpable euphoria on wins or despair on losses) tend to make poorer trading decisions and achieve worse outcomes on average ([Lo et al., 2005](https://doi.org/10.1016/j.jpsychores.2005.07.002)). In contrast, those who maintain more moderate emotional responses perform better, indicating that unchecked emotion often leads to judgment errors. In sum, emotional and physiological biases like fear and over-excitement contribute to **short-term market instability** by causing investors to overreact – either selling off too aggressively in stressful times or buying too exuberantly in frothy times. These human factors can turn information shocks into outsized price swings, as visceral reactions temporarily override analytic reasoning among professional investors.



### 3.2.2 Prospect Theory and Loss Aversion


Prospect theory, as developed by Kahneman and Tversky, posits that individuals exhibit **loss aversion**, meaning losses are felt more acutely than equivalent gains. This framework has important implications in behavioral finance, particularly in how decision-makers react to financial news shocks.

Recent empirical research suggests that **market participants, including professionals**, tend to exhibit **asymmetric overreactions** to negative versus positive information. For example, [Tetlock (2007)](https://academic.oup.com/rfs/article-lookup/doi/10.1093/rfs/hhl079) found that negative media sentiment predicts a temporary drop in daily market returns, with prices typically rebounding shortly afterward—consistent with overreaction to pessimistic news.

Furthermore, [Löffler et al. (2021)](https://onlinelibrary.wiley.com/doi/full/10.1002/jcaf.22493) analyzed reactions to credit rating changes and observed that **downgrades caused price movements up to five times larger** than upgrades. This disproportion highlights how markets penalize bad news more than they reward good news, even in contexts where information is ostensibly symmetric.

Finally, [Neel (2024)](https://doi.org/10.2139/ssrn.4721420) provided cross-country evidence that institutional investors in more loss-averse cultures tend to react more strongly to **negative earnings surprises** than to positive ones. This cultural lens reinforces the systematic nature of asymmetrical reaction patterns and supports the hypothesis that overreaction—particularly in response to loss-related stimuli—is a persistent behavioral feature in financial markets.

Taken together, these findings validate the assumption that **negative financial shocks tend to provoke more immediate and intense market reactions**, a factor highly relevant to the construction and interpretation of the Shock Score.



### 3.2.3 Emotion-Driven Trading and the Disposition Effect

The **disposition effect** refers to the tendency of investors to sell assets that have performed well while retaining assets that have incurred losses, a behavior that leads to **suboptimal portfolio rebalancing**. While initially documented among retail investors, subsequent empirical research demonstrates that the disposition effect is also present among **professional decision-makers**, including mutual fund managers and institutional investors. Using detailed trading records, [Grinblatt and Keloharju (2001)](https://doi.org/10.1111/0022-1082.00308) show that professional investors are more likely to sell winning positions than losing ones, even after controlling for tax considerations and liquidity needs. Similarly, [Frazzini (2006)](https://doi.org/10.1093/rfs/hhj005) finds that mutual fund managers systematically hold on to losing stocks longer than is optimal, leading to predictable underperformance. These findings indicate that emotional attachment to losses and regret avoidance interfere with rational rebalancing decisions, even in institutional settings.

Importantly, the literature suggests that **overreaction to information shocks can reinforce the disposition effect**, rather than correct it. When investors overreact to negative news, prices often decline sharply in the short term, turning previously neutral or profitable positions into paper losses. Loss-averse managers may then delay selling these positions in anticipation of a rebound, thereby locking in exposure to underperforming assets. Conversely, positive news-induced overreaction can inflate short-term gains, prompting premature profit-taking. Empirical evidence supports this mechanism: [Da, Engelberg, and Gao (2011)](https://doi.org/10.1093/rfs/hhq137) show that attention-driven trading around news events increases turnover in winning stocks while leaving losing positions under-adjusted. As a result, emotion-driven trading following information shocks not only amplifies short-term volatility but also **induces systematic rebalancing inefficiencies**, consistent with the disposition effect observed among professional investors.


### 3.2.4 Market Overreaction to Public Information

Recent empirical studies find that stock prices frequently **overshoot in reaction to public news**, especially around earnings announcements and sentiment shocks. For example, [Meng et al. (2024)](https://doi.org/10.1016/j.irfa.2024.101321) document pronounced short-term overreactions to information “jumps” in Chinese stocks, earning sizable profits from contrarian trades as prices subsequently mean-revert. Similarly, [Bahcivan, Dam, and Gonenc (2023)](https://doi.org/10.1016/j.irfa.2023.101297) show a “clear overreaction pattern” following unexpected overnight price jumps in U.S. markets, with statistically significant reversals in the ensuing days. These sharp price swings prove largely temporary: post-shock return predictability is high and contrarian strategies are profitable, indicating partial or full price reversals in the short run. Event studies around earnings and sentiment also confirm this pattern: [Bird et al. (2024)](https://doi.org/10.1016/j.irfa.2023.101314) find that shifts in aggregate investor emotion after earnings news drive persistent price deviations (mispricing), and [McCarthy (2025)](https://doi.org/10.2139/ssrn.4716412) shows that positive surprises that contradict consensus sentiment generate abnormally large drift returns (up to 5–7% over 90 days), reflecting strong confirmation bias and overreaction.

Professional traders and institutional investors often **amplify these misreactions**. [Cremers et al. (2021)](https://doi.org/10.1016/j.jfineco.2021.02.014) report that stocks held by many short-term institutions have especially large announcement-day jumps and subsequent reversals: their outperformance (underperformance) is followed by large negative (positive) future abnormal returns, consistent with overreaction to analyst recommendation changes. In line with this, [Ben-Rephael et al. (2021)](https://doi.org/10.1016/j.jfineco.2020.11.010) find that institutional net buying is positively related to earnings-surprise magnitude (high “REG” scores), implying that funds trade in the same direction as the initial price shock. The resulting volatility can push portfolios away from target allocations and force rebalancing. Indeed, [Harvey, Mazzoleni, and Melone (2025)](https://doi.org/10.2139/ssrn.4716766) show that systematic rebalancing flows by large funds have measurable price effects – for example, when portfolios become overweight equities, selling pressure can depress prices by roughly 17 basis points the next day. In sum, the evidence indicates that news-driven overreactions produce transient mispricings and heightened volatility, creating **significant pressure on portfolio allocation and rebalancing** as managers adjust to the temporary distortions.



### 3.2.5 Synthesis: Behavioral Biases and Portfolio Outcomes

The reviewed literature consistently shows that behavioral biases—particularly overconfidence, availability heuristics, herding, and loss aversion—can distort professional investors’ judgment during information shocks. These biases impair rational processing of news, leading to **overreactions in asset prices**, characterized by short-term volatility spikes and predictable reversals. Even experienced institutional investors are not immune: emotional and cognitive biases alter risk perceptions, induce crowd behavior, and lead to premature or delayed trading decisions.

These distortions have clear implications for portfolio management. Emotional overreactions often result in **suboptimal rebalancing**—such as selling winners too early, holding onto losers too long, or overexposing portfolios to assets that have already experienced sharp price moves. The disposition effect, in particular, illustrates how reluctance to realize losses and eagerness to lock in gains can drag on long-term performance. Moreover, market-wide overreactions propagate through institutional flows, creating **systematic mispricing** that challenges the efficiency of portfolio allocation.

In sum, behavioral biases not only shape price dynamics but also introduce persistent **frictions into the portfolio decision-making process**. Left unmanaged, they reduce the efficiency of risk–return optimization, increase exposure to transient volatility, and ultimately erode investment performance. This synthesis underscores the importance of structured tools—such as Shock Scores or behavioral filters—to mitigate the impact of biases in professional investment settings.


## 3.3 Managerial Decision-Making Under Uncertainty

### 3.3.1 Bounded Rationality and Satisficing Behavior
- Cognitive constraints in complex decision environments
- Limits of optimization under uncertainty

### 3.3.2 Managerial Risk Perception and Framing Effects
- Aspiration levels and survival thresholds
- Deviations from expected utility behavior

### 3.3.3 Optimism, Overconfidence, and Forecasting Errors
- Overestimation of returns and underestimation of risk
- Empirical evidence from corporate investment decisions

### 3.3.4 Risk Versus Uncertainty in Managerial Decisions
- Measurable risk versus fundamental uncertainty
- Implications for judgment-based decision-making

### 3.3.5 Implications for Portfolio and Investment Management

## 3.4 Tools and Methods to Mitigate Emotional and Behavioral Bias

### 3.4.1 Behavioral Finance Prescriptions and Practical Guidance
- Recognition of emotional pitfalls
- Rules-based discipline and pre-commitment mechanisms

### 3.4.2 Choice Architecture and Nudging in Financial Decisions
- Structuring decision environments
- Defaults, reminders, and framing effects

### 3.4.3 Adaptive Markets and Evolutionary Perspectives
- Context-dependent investor behavior
- Flexible strategies and adaptive decision tools

### 3.4.4 From Bias Diagnosis to Bias Mitigation
- Behavioral coaching and decision support
- Education, training, and digital interventions

### 3.4.5 Structured Approaches to Reducing Emotional Bias

## 3.5 Market Reactions to Public Information

### 3.5.1 Efficient Market Hypothesis as a Benchmark
- Rational and instantaneous information processing
- Limitations of market efficiency assumptions

### 3.5.2 Excess Volatility and Sentiment-Driven Markets
- Price movements beyond fundamental justification
- Role of narratives and collective emotion

### 3.5.3 Media Tone, Attention, and Investor Sentiment
- Quantification of news tone and pessimism
- Short-term price and volume reactions

### 3.5.4 Investor Sentiment Indices and Mispricing
- Broad optimism and pessimism cycles
- Differential impact across asset types

### 3.5.5 Information Exposure and Non-Fundamental Trading
- Attention effects independent of content
- Causal impact of media dissemination

## 3.6 Decision-Support Systems in Investment Management

### 3.6.1 Quantitative Foundations of Portfolio Decision Support
- Mean–variance optimization
- Formal risk–return trade-off frameworks

### 3.6.2 Algorithmic and Robo-Advisory Systems
- Automation of portfolio advice
- Benefits and limitations of standardized solutions

### 3.6.3 Decision-Support System Design Principles
- Integration of dynamic data
- Scenario analysis and complexity management

### 3.6.4 Advanced Automated Decision-Support Models
- Information-theoretic asset screening
- Multi-criteria portfolio allocation systems

### 3.6.5 Role of Decision Support in Reducing Emotional Bias

## 3.7 Literature Gap and Research Positioning

### 3.7.1 Limitations of Existing Behavioral Finance Research
### 3.7.2 Gaps in Ex-Ante Decision Support for Information Shocks
### 3.7.3 Positioning of the Shock Score within Existing Literature
### 3.7.4 Summary of Theoretical and Empirical Contributions

-------

# Chapter 4. Collection of Primary Data

## 4.1 Chapter Introduction

## 4.2 Research Design
### 4.2.1 Research Paradigm
### 4.2.2 Conceptual Framework
### 4.2.3 Independent and Dependent Variables

## 4.3 Research Instrument
### 4.3.1 News Data Sources and Selection Criteria
### 4.3.2 Sentiment Scoring Methodology
### 4.3.3 Event-Type Classification Logic
### 4.3.4 Construction of the Shock Score

## 4.4 Population and Sample
### 4.4.1 Portfolio Universe
### 4.4.2 Observation Period and Frequency

## 4.5 Sampling Technique
### 4.5.1 Selection of Events and Decision Windows

## 4.6 Data Collection Process
### 4.6.1 Data Cleaning and Preprocessing
### 4.6.2 Alignment of News and Portfolio Data

## 4.7 Descriptive Statistics
### 4.7.1 Descriptive Statistics of Shock Scores
### 4.7.2 Descriptive Statistics of Portfolio Outcomes

## 4.8 Chapter Conclusion

# Chapter 5. Analysis and Conclusions

## 5.1 Chapter Introduction

## 5.2 Hypothesis Testing
### 5.2.1 Testing of Hypothesis H₁
### 5.2.2 Testing of Hypothesis H₂

## 5.3 Results Interpretation
### 5.3.1 Impact of Information Shocks on Risk–Return
### 5.3.2 Incremental Effect of the Shock Score

## 5.4 Interim Conclusions

## 5.5 Chapter Conclusion

# Chapter 6. Conclusions and Recommendations

## 6.1 Chapter Introduction

## 6.2 Summary of Findings
### 6.2.1 Summary of Secondary Research
### 6.2.2 Summary of Primary Research

## 6.3 Overall Conclusions

## 6.4 Recommendations
### 6.4.1 Recommendations for Portfolio Managers
### 6.4.2 Recommendations for Risk Governance

## 6.5 Areas for Future Research

## 6.6 Lessons Learned

## 6.7 Ethical Considerations
### 6.7.1 Ethical Use of Algorithmic Decision Support
### 6.7.2 Risk of Automation Bias

## 6.8 Implications for Sustainable Development Goals
### 6.8.1 Responsible Decision-Making in Financial Markets

## 6.9 Chapter Conclusion

# Back Matter

- Glossary
- References
- Appendix A. Thesis Approval Form
- Appendix B. Blank Questionnaire / Instrument
- Appendix C. Additional Supporting Material
