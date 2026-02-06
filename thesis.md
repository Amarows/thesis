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
-------------------------------
# Chapter 3. Literature Review

>The literature review is designed to bridge foundational behavioral finance theory with applied challenges in professional investment decision-making, culminating in the rationale for structured debiasing tools.

## 3.1 Link Between Literature and Research Hypotheses

>This introductory section defines key theoretical constructs (e.g., information shocks, behavioral bias, Shock Score) and explains their relevance to the research problem.

The research hypotheses in this study draw on key concepts from behavioral finance and decision-making literature, focusing on how information shocks affect market behavior. An **information shock** refers to publicly available news or updates related to individual stocks that generate a material short-term market reaction, typically observable at a daily frequency. Such shocks are characterized by their ability to affect short-term price dynamics and volatility without necessarily changing the long-term fundamentals of the underlying firm, and therefore, firm valuation.

The literature suggests that information shocks influence market prices through behavioral and emotional biases. Empirical evidence demonstrates that investors and managers frequently overreact to salient or emotionally charged news due to cognitive and affective biases, leading to temporary price distortions rather than rational revaluation based on fundamentals.

The Shock Score introduced in this thesis is motivated by existing research on sentiment, attention, and volatility-based measures of market reaction. It quantifies the emotional intensity of an information shock by capturing abnormal short-term market responses, such as excess daily volatility, that arise from behavioral reactions rather than fundamental reassessment.

While the literature contains several indices and measures aimed at capturing market sentiment or uncertainty, such as sentiment indices or news-based volatility indicators, there is limited evidence of tools specifically designed to support managerial decision-making at the time of an information shock. This gap motivates the development and empirical testing of the Shock Score as a decision-support mechanism intended to improve investment decisions by reducing behavioral overreaction.

---

## 3.2 Behavioral Biases in Investment Decision-Making

>This section surveys behavioral finance theory—how cognitive biases like overconfidence, loss aversion, disposition effect, and emotional trading shape investor behavior. It integrates psychological theory and empirical findings with a focus on market reactions and volatility.

### 3.2.1 Heuristics and Judgment Under Uncertainty

Professional investors, despite their expertise, are not immune to the cognitive shortcuts and biases that affect human judgment under uncertainty. In fact, several prevalent biases – **overconfidence**, **availability and recency bias**,**herding**, and **emotional/physiological biases** – can cause even expert decision-makers to react in ways that amplify short-term market volatility and lead to overreactions to financial information shocks. Below we discuss each of these biases and their impact on short-term market dynamics.

Overconfidence is a well-documented cognitive bias in which individuals exhibit unwarranted faith in the accuracy of their own judgments and beliefs ([Moore & Healy, 2008](https://doi.org/10.1037/0033-295X.115.2.502)). In the finance literature, overconfidence manifests in excessive trading and systematic overestimation of predictive ability. Barber and Odean (2001) provide empirical evidence that investors exhibiting higher inferred overconfidence trade more frequently and earn lower risk-adjusted returns, a pattern consistent with overconfidence-driven misjudgment ([Barber & Odean, 2001](https://doi.org/10.1162/003355301556400)).

This bias manifests even among professionals – for example, successful traders and fund managers may become overconfident in their skill, particularly after a streak of good performance ([Gervais & Odean, 2001](https://doi.org/10.1093/rfs/14.1.1)). Overconfidence leads investors to underweight risks and to trade more aggressively than rational benchmarks would predict, often to their own detriment ([Odean, 1999](https://doi.org/10.1257/aer.89.5.1279)). Theoretical models show that overconfident investors can introduce excess volatility into markets by overreacting to new information: prices may move more than fundamentals justify due to overly aggressive trading on private signals, generating short-run momentum that later reverses ([Daniel et al., 1998](https://doi.org/10.1111/0022-1082.00077)). In essence, overconfidence can cause initial overreactions to news followed by subsequent reversals once information is corrected, thus contributing significantly to short-term market volatility.



Another class of bias arises from the heuristics investors use to judge the importance of information. The availability heuristic refers to the tendency to assess the probability or relevance of an event based on how easily examples come to mind ([Tversky & Kahneman, 1974](https://www.science.org/doi/10.1126/science.185.4157.1124)). In practice, this implies that vivid or recent information often dominates decision-making because it is readily recalled, even if it is not objectively more informative. A closely related phenomenon is recency bias – the inclination to give disproportionately high weight to the most recent events or data points when forming judgments. Evidence in behavioral finance indicates that investors and other decision-makers tend to overweight recent outcomes relative to earlier information, thereby distorting expectations ([Hirshleifer, 2015](https://doi.org/10.1146/annurev-financial-092214-043752)). Even seasoned professionals are susceptible: mutual fund managers have been shown to extrapolate their fund’s recent performance into their outlook for the overall market, effectively basing forecasts on the latest returns rather than long-term fundamentals ([Azimi, 2019](https://doi.org/10.2139/ssrn.3462776)). Such availability and recency biases can amplify short-term volatility by fueling overreactions to salient news, as prices may temporarily overshoot intrinsic values before expectations adjust.



Herding describes the tendency of investors to mimic the actions of others instead of relying on their own independent analysis. In uncertain environments, even professional investors often follow the crowd – for instance, by buying or selling a stock simply because many of their peers are doing so – assuming that the collective might know better or as a form of career risk management (it may feel safer to err in a crowd than to err alone) ([Scharfstein & Stein, 1990](https://www.hbs.edu/ris/Publication%20Files/Herd%20Behavior%20and%20Investment_1f30fd71-a48f-4751-b267-ba97ec9b6160.pdf); [Bikhchandani et al., 1992](https://doi.org/10.1086/261849)). In formal terms, herd behavior occurs when investors follow or copy others’ investment decisions rather than act on their private information. The herding heuristic can amplify short-term market movements: coordinated buying may push prices above fundamentals (and coordinated selling below). Empirical evidence indicates that herding-induced price pressures can be short-lived: stocks persistently bought by institutions tend to earn negative subsequent returns as prices correct, while persistently sold stocks tend to rebound ([Dasgupta et al., 2011](https://doi.org/10.1093/rfs/hhq137); [Brown et al., 2014](https://doi.org/10.1287/mnsc.2013.1751)). Accordingly, herding by professional investors can contribute to short-run price instability and volatility around information events.



Beyond cognitive heuristics, emotional and physiological factors can heavily influence investors’ judgment under stress. Professional decision-makers are not emotionless agents; feelings such as fear, greed, anxiety, or over-excitement can bias choices, particularly during market shocks. Research documents that acute stress and arousal can impair decision-making even in expert traders ([Lo et al., 2005](https://www.aeaweb.org/articles?id=10.1257/000282805774670095); [Coates & Herbert, 2008](https://doi.org/10.1073/pnas.0704025105)). During periods of market turmoil, fear can trigger a physiological stress response that inclines investors to flee from risk. Elevated cortisol levels have been shown to correspond with such conditions; under high cortisol, traders become more risk-averse, potentially intensifying sell-offs ([Coates & Herbert, 2008](https://doi.org/10.1073/pnas.0704025105)). Conversely, in euphoric markets, testosterone-linked increases in confidence and risk-taking may reinforce speculative behavior; excessive levels can foster reckless overconfidence (Coates, 2010, The winner effect: Testosterone, cortisol and the risk of financial bubbles). Evidence further indicates that traders exhibiting extremely intense emotional reactions tend to make poorer trading decisions and achieve worse outcomes on average ([Lo et al., 2005](https://www.aeaweb.org/articles?id=10.1257/000282805774670095)). In sum, emotional and physiological biases contribute to short-term market instability by driving overreactions to information shocks.




### 3.2.2 Prospect Theory and Loss Aversion

Prospect theory, as developed by Kahneman and Tversky, posits that individuals exhibit loss aversion, meaning that losses are experienced more intensely than gains of equal magnitude ([Kahneman & Tversky, 1979](https://doi.org/10.2307/1914185)). This framework has important implications for behavioral finance, particularly in shaping how decision-makers respond to financial news shocks.

Empirical research further suggests that market participants, including professional investors, exhibit asymmetric reactions to negative versus positive information. For example, Tetlock (2007) finds that negative media sentiment predicts a temporary decline in daily market returns, with prices typically rebounding shortly thereafter, a pattern consistent with overreaction to pessimistic news ([Tetlock, 2007](https://doi.org/10.1111/j.1540-6261.2007.01232.x)).

Furthermore, Löffler et al. (2021) analyze market reactions to credit rating changes and show that downgrades trigger substantially larger price movements than upgrades. This pronounced asymmetry indicates that markets penalize negative credit news far more strongly than they reward positive revisions, even when the underlying informational content is comparable ([Löffler et al., 2021](https://doi.org/10.1016/j.jbankfin.2021.106256)).

Finally, Neel (2024) provides cross-country evidence that institutional investors operating in more loss-averse cultural environments react more strongly to negative earnings surprises than to positive ones ([Neel, 2024](https://doi.org/10.1142/S1094406024500215)). This cultural perspective reinforces the systematic nature of asymmetric reaction patterns and supports the view that overreaction—particularly in response to loss-related information—is a persistent behavioral feature of financial markets.

Taken together, these findings validate the assumption that negative financial shocks tend to provoke more immediate and intense market reactions, a factor highly relevant to the construction and interpretation of the Shock Score.




### 3.2.3 Emotion-Driven Trading and the Disposition Effect


The disposition effect refers to the tendency of investors to sell assets that have performed well while retaining assets that have incurred losses, a behavior that leads to suboptimal portfolio rebalancing. While initially documented among retail investors, subsequent empirical research demonstrates that the disposition effect is also present among professional decision-makers, including institutional investors. Using detailed trading records, Grinblatt and Keloharju (2001) show that investors are more likely to sell winning positions than losing ones, even after controlling for tax considerations and liquidity needs ([Grinblatt & Keloharju, 2001](https://doi.org/10.1111/0022-1082.00338)). Similarly, Frazzini (2006) finds that the disposition effect contributes to underreaction to news and predictable return patterns, consistent with investors holding losing positions too long and realizing losses too slowly ([Frazzini, 2006](https://doi.org/10.1111/j.1540-6261.2006.00896.x)). These findings indicate that regret avoidance and emotional attachment to losses can interfere with rational rebalancing decisions even in institutional settings.



Importantly, the literature suggests that overreaction to information shocks can reinforce the disposition effect rather than correct it. When investors overreact to negative news, prices often decline sharply in the short term, turning previously neutral or profitable positions into paper losses. Loss-averse managers may then delay selling these positions in anticipation of a rebound, thereby maintaining exposure to underperforming assets. Conversely, positive news-induced overreaction can inflate short-term gains, prompting premature profit-taking. Empirical evidence supports this mechanism: Da, Engelberg, and Gao (2011) show that attention-driven trading around news events increases turnover in attention-grabbing stocks, consistent with a stronger propensity to trade recent winners and delayed adjustment in losers ([Da et al., 2011](https://doi.org/10.1111/j.1540-6261.2011.01679.x)). As a result, emotion-driven trading following information shocks not only amplifies short-term volatility but also induces systematic rebalancing inefficiencies consistent with the disposition effect.




### 3.2.4 Market Overreaction to Public Information

### 3.2.4 Market Overreaction to Public Information

Recent empirical evidence indicates that stock prices frequently overshoot in response to public information shocks, leading to temporary mispricing and subsequent reversals. Using event-based analysis, recent research documents that sharp price movements following public news often exceed what can be justified by fundamentals and are partially corrected in the days that follow, consistent with investor overreaction rather than efficient price adjustment ([Meng et al., 2024](https://doi.org/10.1016/j.irfa.2024.103219)). 

These findings imply that public information shocks can generate short-term volatility and return predictability, as initial reactions reflect behavioral biases such as salience and confirmation rather than fully rational updating. As prices gradually revert toward intrinsic values, contrarian strategies become profitable, reinforcing the interpretation of these dynamics as overreaction-driven market responses.


Professional traders and institutional investors can amplify these misreactions. Cremers, Pareek, and Sautner (2021) show that stocks with high short-term institutional ownership exhibit especially large announcement-day price reactions and subsequent reversals around analyst recommendation changes: prior outperformance (underperformance) is followed by negative (positive) future abnormal returns, consistent with overreaction ([Cremers et al., 2021](https://doi.org/10.1111/1475-679X.12352)).

In a related setting, Ben-Rephael et al. (2022) document that institutional trading around earnings announcements is strongly aligned with the magnitude of the initial price reaction, indicating that institutions tend to trade in the same direction as the earnings-day shock rather than correcting it ([Ben-Rephael et al., 2022](https://dx.doi.org/10.2139/ssrn.3966758)). Such synchronized trading behavior can exacerbate short-term volatility and push portfolios away from target allocations.

Systematic rebalancing flows further transmit these shocks into prices. Harvey, Mazzoleni, and Melone (2025) show that mechanical rebalancing by large asset managers generates statistically significant short-term price pressure; for example, when portfolios become overweight equities, subsequent selling pressure depresses equity returns by approximately 17 basis points on the following day ([Harvey et al., 2025](https://doi.org/10.2139/ssrn.5122748)). Taken together, the evidence indicates that news-driven overreactions by institutional investors produce transient mispricings and heightened volatility, creating significant pressure on portfolio allocation and rebalancing decisions.





### 3.2.5 Synthesis: Behavioral Biases and Portfolio Outcomes

The reviewed literature consistently shows that behavioral biases—particularly overconfidence, availability heuristics, herding, and loss aversion—can distort professional investors’ judgment during information shocks. These biases impair rational processing of news, leading to **overreactions in asset prices**, characterized by short-term volatility spikes and predictable reversals. Even experienced institutional investors are not immune: emotional and cognitive biases alter risk perceptions, induce crowd behavior, and lead to premature or delayed trading decisions.

These distortions have clear implications for portfolio management. Emotional overreactions often result in **suboptimal rebalancing**—such as selling winners too early, holding onto losers too long, or overexposing portfolios to assets that have already experienced sharp price moves. The disposition effect, in particular, illustrates how reluctance to realize losses and eagerness to lock in gains can drag on long-term performance. Moreover, market-wide overreactions propagate through institutional flows, creating **systematic mispricing** that challenges the efficiency of portfolio allocation.

In sum, behavioral biases not only shape price dynamics but also introduce persistent **frictions into the portfolio decision-making process**. Left unmanaged, they reduce the efficiency of risk–return optimization, increase exposure to transient volatility, and ultimately erode investment performance. This synthesis underscores the importance of structured tools—such as Shock Scores or behavioral filters—to mitigate the impact of biases in professional investment settings.

---

## 3.3 Managerial Decision-Making Under Uncertainty

>Here, the focus shifts to professional investors and managers operating under real-world constraints: bounded rationality, organizational pressure, and framing effects. It shows how even experts -- despite training -- make predictably biased decisions under uncertainty.

### 3.3.1 Why Bias Persists Despite Experience

Even seasoned, well-incentivized managers continue to rely on heuristic shortcuts in decision-making, underscoring the limits of human rationality. Bounded rationality—a concept introduced by Simon (1955)—posits that individuals face inherent constraints in cognitive capacity and information processing and therefore satisfice (seek a good-enough option) rather than optimally solve complex problems ([Simon, 1955](https://doi.org/10.2307/1884852)). In practice, this implies that even professional managers with extensive training cannot exhaustively evaluate all alternatives or anticipate every possible outcome. Instead, they rely on experience-based rules of thumb and intuitive judgments, particularly under time pressure. While such heuristics facilitate decision-making, they also embed systematic biases—such as overconfidence or anchoring—that persist despite expertise.


High-stakes managerial environments often exacerbate this reliance on heuristics. Real-world portfolio and strategic decisions are typically made under tight time constraints and uncertain information, making exhaustive rational evaluation infeasible. The cognitive effort required to weigh all possible options and outcomes is prohibitive when markets move quickly or when a flood of data must be processed in real time. Thus, even rational, incentivized managers resort to mental shortcuts as a practical response to complexity and time pressure (Simon, 1955; [Simon, 1955](https://doi.org/10.2307/1884852)). This boundedly rational behavior is not due to lack of knowledge or effort, but a reflection of human information-processing limits. Unfortunately, the very shortcuts that make decision-making manageable can systematically skew perceptions of risk and return.

Crucially, research shows that experience and expertise alone do not eliminate biases. In a classic study, Hodgkinson et al. (1999) show that framing can materially shift risky choices in strategic decision contexts, indicating that such effects can persist even among decision-makers with substantial managerial exposure ([Hodgkinson et al., 1999](https://doi.org/10.1002/(SICI)1097-0266(199910)20:10%3C977::AID-SMJ58%3E3.0.CO;2-X)). Likewise, Ben-David, Graham, and Harvey (2013) find that CFOs and other financial professionals produce severely miscalibrated forecasts, with confidence intervals that are far too narrow relative to realized market outcomes ([Ben-David et al., 2013](https://doi.org/10.1093/qje/qjt023)). March and Shapira (1987) also find that many managers perceive themselves as less risk-averse than their peers and view risk as largely controllable through skill and information, consistent with overconfidence and an illusion of control ([March & Shapira, 1987](https://doi.org/10.1287/mnsc.33.11.1404)). In short, professional training may raise awareness, but it does not fully immunize managers against bias in how they perceive and act on risky decisions.

The persistence of bias is clearly evident in professional portfolio management as well. Behavioral finance research has documented that even institutional investors and fund managers exhibit many of the same biases as retail investors. For instance, extrapolation and optimism biases can lead market participants to overweight recent winners in their expectations and take on excessive risk, a pattern that can backfire when prices mean-revert and subsequent returns disappoint ([Baker & Wurgler, 2007](https://doi.org/10.1257/jep.21.2.129)). Similarly, overconfidence is common: trading evidence shows that biased confidence drives frequent, costly trades and lower net performance ([Barber & Odean, 2001](https://doi.org/10.1162/003355301556400)). Professional decision-makers are also prone to herding and loss aversion, contributing to under-diversified portfolios and suboptimal investment timing ([Statman, 2019](https://doi.org/10.2139/ssrn.3668963)).

In conclusion, knowing about cognitive biases is not, by itself, sufficient to guarantee unbiased decisions. Decades of research and practical experience indicate that psychological insight must be complemented by structured decision support to meaningfully improve judgment. Kahneman et al. (2021) argue that biases and noise cannot be reliably corrected through individual awareness alone and that organizations should instead rely on structured decision processes, rules, and judgment aggregation procedures to improve decision quality ([Kahneman et al., 2021](https://hbr.org/2016/10/noise)). In other words, mitigating bias requires more than awareness or good intentions; it demands systematic support tools and procedures that guide managers toward more rational and consistent choices. This need for structured debiasing mechanisms motivates the analysis in Section 3.4, which examines how decision-support frameworks can be designed to counteract persistent biases in managerial decision-making.



### 3.3.2 Situational Risk Preferences in Practice

Empirical studies show that professional decision-makers often become risk-seeking when performance falls short of an aspiration or target. In line with prospect theory intuition, a fixed target acts as a reference point: when results are below the aspiration level, managers shift into the loss domain and tend to take on more risk to recover ([March & Shapira, 1987](https://doi.org/10.1287/mnsc.33.11.1404)). 

Consistent with this logic, Wiseman and Gomez-Mejia (1998) develop a behavioral agency framework in which performance below aspirations increases the propensity for risk taking, particularly as decision-makers approach distress thresholds ([Wiseman & Gomez-Mejia, 1998](https://doi.org/10.5465/AMR.1998.192967)). Similarly, Wennberg, Delmar, and McKelvie (2016) provide entrepreneurship evidence consistent with variable risk preferences: risk-taking responses depend on performance feedback relative to aspiration levels, with behavior changing materially when outcomes fall below benchmarks ([Wennberg et al., 2016](https://doi.org/10.1016/j.jbusvent.2016.05.001)). These findings suggest that framing outcomes relative to benchmarks can flip risk preferences in practice.


Empirical studies show that professional decision-makers often become risk-seeking when performance falls short of an aspiration or target. In line with prospect theory intuition, a fixed target acts as a reference point: when outcomes fall below the aspiration level, managers enter the loss domain and tend to increase risk-taking in an attempt to recover losses ([March & Shapira, 1987](https://doi.org/10.1287/mnsc.33.11.1404)).


Consistent with this view, Wiseman and Gomez-Mejia (1998) show that organizations experiencing poor performance become more willing to take risks as outcomes fall below aspiration levels, particularly as firms approach critical thresholds such as financial distress or bankruptcy ([Wiseman & Gomez-Mejia, 1998](https://doi.org/10.5465/AMR.1998.192967)). 

Similarly, Wennberg, Delmar, and McKelvie (2016) provide entrepreneurship evidence that risk preferences are variable rather than fixed: decision-makers behave in a relatively risk-averse manner when performance meets or exceeds aspirations but become more risk-seeking once outcomes fall below benchmark levels ([Wennberg et al., 2016](https://doi.org/10.1016/j.jbusvent.2016.05.001)). These findings indicate that framing outcomes relative to aspiration benchmarks can systematically flip risk preferences, even in the absence of explicit incentive changes.



Importantly, these biases often intensify during market downturns, despite managers’ professional training. Behavioral evidence from controlled experiments indicates that during the COVID-19 market crash, finance professionals significantly reduced their allocations to risky assets even though fundamentals and price expectations remained unchanged—a pattern consistent with heightened situational risk aversion under stress ([Huber et al., 2021](https://www2.uibk.ac.at/downloads/c9821000/wpaper/2020-11.pdf)). This finding suggests that acute stress and fear during sharp market declines can override logical planning and that emotional pressures may amplify risk preferences even among experienced decision-makers.


### 3.3.3 Portfolio-Level Implications

These situational biases often translate into suboptimal portfolio decisions. Herding and trend-chasing may creep into rebalancing practices, and stress can push professionals toward procyclical behavior consistent with “buying high and selling low.” Physiological evidence shows that emotional arousal and stress measurably affect professional traders’ real-time risk processing, helping explain panic-like trading under pressure ([Lo & Repin, 2002](https://doi.org/10.1162/089892902317361877)).

Consistent with this mechanism, Elkind et al. (2022) show that extreme market conditions trigger panic selling and rapid exits rather than disciplined rebalancing, leading to excessive turnover and destabilizing price pressure ([Elkind et al., 2022](https://doi.org/10.3905/JFDS.2021.1.085)). Under stress, managers may also de-risk portfolios for non-fundamental reasons. For example, fund managers reduce risk exposure by nearly 9 percent during culturally “unlucky” periods, highlighting how non-financial pressures and superstition can induce systematic allocation errors ([Chen et al., 2024](http://doi.org/10.2139/ssrn.4942370).


Given the persistence of these effects, researchers emphasize the need for structured tools and procedures to improve decision quality. Bianchi et al. (2023) show that automated advice platforms, such as robo-advisors, help attenuate behavioral biases including loss aversion and anchoring by constraining discretionary judgment and enforcing consistent decision rules ([Bianchi et al., 2023](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4501864)). Complementary work recommends rule-based protocols—such as fixed-schedule rebalancing or performance-triggered adjustments—as a way to limit emotional interference in portfolio decisions ([Statman, 2019](https://doi.org/10.2139/ssrn.3668963)). In summary, structured tools and disciplined procedures, rather than intuition alone, are required to help even professional investors avoid persistent cognitive traps.


============================================================
---

## 3.4 Tools to Mitigate Emotional and Behavioral Bias

>This section reviews structured interventions, such as decision-support systems, quantitative overlays, and behavioral coaching. It presents empirical evidence on how such tools help mitigate bias and improve portfolio performance.

### 3.4.1 Rule-Based Approaches and Pre-Commitment Mechanisms

Many advisors use structured plans and decision rules to curb emotion-driven trading. For example, drafting an **Investment Policy Statement (IPS)** that defines goals, risk limits, and rebalancing rules can “put an objective framework around portfolio management” and help reduce emotional reactions([Statman, 2019](https://doi.org/10.2139/ssrn.3668963)). Pre-commitment devices—like automatic rebalancing schedules, stop-loss or profit-taking triggers—shift decisions from being reactive to procedural. Research suggests that “the most effective way to reduce emotional reactivity is to commit in advance to specific decision rules,” since these rules are followed even when emotions run high([Shefrin, 2002](https://books.google.com/books/about/Beyond_Greed_and_Fear.html?id=hX18tBx3VPsC)).

While effective for discipline, these tools rely entirely on consistent human adherence. Their effectiveness diminishes under high emotional strain, market crises, or cognitive overload.


### 3.4.2 Automated and AI-Driven Approaches

Beyond static rules, automation can remove human emotion from trading. Robo-advisors and algorithmic systems base decisions on data and preset models, “de-humanizing” portfolio reactions and helping investors maintain alignment with long-term strategy ([Jung et al., 2018](https://doi.org/10.2139/ssrn.3124820);[Baker & Dellaert, 2022](https://doi.org/10.1007/s10603-022-09520-1)). Algorithmic portfolios buy or sell according to predefined logic, regardless of investor panic or euphoria.

That said, automated systems have limits. They rely on historical data and user-supplied inputs (e.g. risk preferences), which may carry their own biases. Furthermore, they may not adapt well to novel or ambiguous situations. To address this, researchers advocate combining automation with human oversight, explainable AI (XAI), and robust audit mechanisms ([Bracke et al., 2019](https://www.bankofengland.co.uk/working-paper/2019/explainability-and-its-limits-in-the-uses-of-ai)).

In practice, some firms deploy NLP-based tools to flag potential biases—such as anchoring or herd language—in analyst reports or news feeds ([Kazemian et al., 2023](https://doi.org/10.1016/j.jbef.2022.100774)). These alerts serve as real-time nudges, but still require expert interpretation.

---

### 3.4.3 Quantifying Bias: Metrics and Behavioral Factor Models

A critical advancement is the quantitative measurement of biases. Recent reviews have identified up to 11 key behavioral biases (e.g., disposition effect, overtrading, trend chasing) and 29 empirical proxies to track them in professional portfolios ([Duxbury & Summers, 2022](https://doi.org/10.1016/j.jbef.2021.10070)). Common proxies include portfolio turnover, concentration ratios, and deviation from benchmark weights.

---

## 3.5 Implications for Portfolio Management
>This section consolidates insights from 3.1 to 3.4, linking behavioral theory and empirical finance with practical investment strategy. It explains how unmanaged bias degrades portfolio quality and why measurement-based tools like the Shock Score may help restore decisio efficiency.

Investment professionals, like all decision-makers, face **bounded rationality** and use mental shortcuts when processing complex market information. They cannot evaluate every piece of data fully, so they rely on heuristics and frames to simplify decisions ([Simon, 1955](https://doi.org/10.2307/1884852); [Statman, 2019](https://doi.org/10.2139/ssrn.3668963)). Even experts exhibit systematic biases: for example, portfolio managers can become anchored to initial price levels and overconfident in their forecasts ([Ben-David et al., 2013](https://doi.org/10.1093/rfs/hhs068)). Cognitive framing also distorts judgments—identical information can lead to different choices depending on how it is presented. In sum, these cognitive limits and framing effects cause persistent errors (e.g., home bias, under-diversification, disposition effects) that degrade portfolio performance.

These biases are magnified under **market shocks and stress**. Acute uncertainty impairs deliberative reasoning and shifts managers toward intuition and habit, thereby amplifying heuristics and framing biases ([Lo, 2004](https://doi.org/10.3905/jpm.2004.442611); [Kahneman & Lovallo, 1993](https://doi.org/10.1287/mnsc.39.1.17)). Empirical studies of COVID‑19 and other crises show that investors (including professionals) reacted emotionally to news—overreacting or herding in response to infection or policy announcements ([Baker et al., 2020](https://doi.org/10.1016/j.jfineco.2020.06.013)). The resulting volatility spikes and crowd behavior are well documented. In fact, volatility following an information shock tends to remain elevated for a prolonged period ([Barunik & Kley, 2019](https://doi.org/10.1016/j.jeconom.2019.03.006)), keeping stress high and reinforcing biased reactions. Thus, bounded rationality combined with stress and framing effects produces persistent portfolio errors during shocks.

The implication for portfolio management is that human decision-making alone is often **insufficiently consistent**. Behavioral factor models find that biases like trend-chasing and overtrading measurably harm performance ([Duxbury & Summers, 2022](https://doi.org/10.1016/j.jbef.2021.100701)). Even sophisticated institutions are not immune: analysts and fund managers routinely exhibit overconfidence, loss aversion, and herd behavior ([Ben-David et al., 2013](https://doi.org/10.1093/rfs/hhs068)). Consciously combating bias through training or rules of thumb has limited impact, especially when stress is high. Therefore, modern practice increasingly supplements human judgment with structured tools and algorithms. Advanced dashboards, real-time analytics, and AI models can systematically counteract cognitive limits by surfacing objective signals and alerts ([Statman, 2019](https://doi.org/10.2139/ssrn.3668963); [Bianchi et al., 2023](https://doi.org/10.2139/ssrn.4501864)). For example, AI-driven monitoring systems synthesize market data into clear risk indicators, preventing late or emotional reactions.

In this context, there is a clear need for a quantitative shock indicator. Just as researchers distinguish news-driven “information shocks” from pure volatility shocks ([Rigobon, 2003](https://doi.org/10.1016/S0304-3932(03)00096-6)), a **Shock Score** would quantify the magnitude of new, unexpected information hitting the portfolio. This objective metric could trigger disciplined responses (e.g., reducing leverage or rebalancing according to predefined rules) exactly when managers might otherwise panic or cling to outdated assumptions. Prior work has shown the value of similar constructs—for instance, a “sentiment shock score” has been used to capture extreme news-driven sentiment swings in stock trading ([Engelberg & Parsons, 2011](https://doi.org/10.1111/j.1540-6261.2011.01666.x)). By explicitly measuring shock intensity, the Shock Score aims to improve decision consistency across turbulent markets. In sum, the literature shows that persistent emotional biases and stress-induced errors undermine portfolio choices, motivating automated checks and new tools (like the Shock Score) to guide more stable decisions.

## 3.6 Limitations in Behavioral Finance Research

>This final section defines what is not known and explicitly justifies  research contribution. It ensures academic rigor by clarifying how  thesis builds upon, diverges from, or fills existing gaps in the literature.
> 
### 3.6.1 Limitations of Existing Behavioral Finance Research

Behavioral finance has produced extensive evidence of biases in investment decisions, but much of this literature remains descriptive and ex-post. Many studies rely on laboratory or retrospective data, with limited guidance for forward-looking decision making. For example, [Bhandari et al. (2008)](https://doi.org/10.1016/j.dss.2007.09.001) note that despite growing awareness of psychological factors, existing financial decision-support systems (DSS) “are still on providing quantitative support (e.g. computation of fundamentals, risks and trends), and not debiasing.” In other words, academic findings about biases have not been systematically integrated into practical tools or investment models.

Another key limitation is the lack of professional context. Behavioral experiments often use students or lay investors rather than actual portfolio managers, raising concerns about external validity. Recent reviews underscore these concerns. [Huber et al. (2024)](https://www.sciencedirect.com/science/article/abs/pii/S0167268123003324) systematically analyzed over 50 studies comparing financial professionals to laypeople and found that professionals are not simply “superforecasters” – they tend to be more risk-loving, yet show no clear forecasting advantage. In other words, financial experts do exhibit biases (and respond to incentives differently), but much of the behavioral literature implicitly assumes “naïve” investors or students. Similarly, [Huber, Jürgen & Kirchler (2022)](https://doi.org/10.1016/j.joep.2021.102512) find that professionals and students react differently to volatility shocks: professionals’ perceived risk rises similarly after any shock, whereas students’ risk perception is driven mainly by negative returns frequency. These findings highlight that results from homogeneous or student samples may not generalize to experienced portfolio managers. In sum, existing research often under-represents real-world investment professionals and may fail to capture how they actually behave under stress.

A further limitation is the lack of ex-ante applicability. Most behavioral studies document biases after they occur (ex-post) or in static, artificial tasks, rather than offering predictive models of behavior. As a result, portfolio managers have few tools to anticipate when biases will strike. The literature rarely provides forward-looking decision rules or adaptive strategies that managers could use before or during an information event. In practice, this means cognitive and emotional factors remain “latent” risks: they are identified in hindsight but are difficult to incorporate into pre-emptive risk management or decision support. Existing asset-pricing or risk models typically ignore these human factors entirely. In summary, current behavioral finance research is rich in identifying anomalies but offers limited guidance on how to integrate these insights into dynamic decision-support systems for practitioners, especially on an ex-ante (anticipatory) basis.

### 3.6.2 Gaps in Ex-Ante Decision Support for Information Shocks

Information shocks – sudden news events such as earnings releases, policy announcements, or geopolitical news – pose a significant challenge for portfolio managers. Although behavioral finance recognizes that investors often overreact or underreact to such events, most academic models and tools do not prepare managers in advance. Conventional decision support and risk-management systems focus on quantitative factors (e.g. volatility, correlations) and static optimization, but typically ignore the real-time psychological state of decision-makers. [Lim (2025)](https://doi.org/10.2139/ssrn.4706208) points out that “conventional rule-based advisory systems typically overlook investor psychology and real-time sentiment dynamics, limiting their effectiveness” during market stress. In other words, current advisory platforms and risk dashboards do not alert managers to their own cognitive vulnerabilities as a shock unfolds.

Moreover, the existing literature lacks frameworks or algorithms for adaptive decision support under uncertainty. There are very few tools that can adjust recommendations on the fly in response to behavioral cues or sentiment shifts. For instance, [Song et al. (2015)](https://doi.org/10.2139/ssrn.2544443) developed a “sentiment shock score” to capture extreme news-driven sentiment for trading strategies, but this approach targets algorithmic signals for asset returns rather than providing guidance to human managers. No mainstream system translates incoming information into a personalized caution signal or bias-mitigation advice. In practice, portfolio managers often rely on judgment or static heuristics (e.g. sticking to asset allocation) when headlines break, with little real-time support. Thus, there is a clear gap: while technological advances (e.g. NLP, AI) could in principle track news and trader sentiment in real time, academic research and commercial tools have not yet produced a behavioral “early warning system” for shocks. Current models remain largely backward-looking (assessing past returns or volatility) and fail to address how a manager’s psychology should adapt as new information arrives.

In sum, existing decision-support tools are dynamic in price/risk metrics but static in psychological terms. They do not incorporate the behavioral feedback loop that occurs during crises: once a shock hits, managers’ biases and emotions change, potentially derailing strategies. This deficiency has become more critical as markets have accelerated: in 2020–2025, news and social media can move prices in minutes, but studies on corresponding decision aids are scarce. In short, behavioral finance has yet to deliver robust ex-ante decision support for information shocks, revealing a major gap between theory and portfolio practice.

### 3.6.3 Positioning of the Shock Score within Existing Literature

The Shock Score concept introduced in this thesis is novel in that it explicitly bridges the gap between behavioral theory and operational needs. Unlike most behavioral studies, the Shock Score is designed as an ex-ante, real-time metric. It quantifies the potential cognitive strain on a portfolio manager before and during an information event, integrating market data with psychological factors. To our knowledge, no prior work has created a similar behavioral risk index tailored for practitioners. (The closest analogies are technical: e.g., [Song et al. (2015)](https://doi.org/10.2139/ssrn.2544443) constructed a sentiment-based shock score to predict asset returns, but this is aimed at algorithmic trading and not at guiding human decisions.) By contrast, the Shock Score applies insights from cognitive psychology (such as loss aversion, anchoring, overconfidence, and others) to generate an actionable signal.

This approach aligns with recent calls in the literature. For example, [Lim (2025)](https://doi.org/10.2139/ssrn.4706208) demonstrates the value of combining behavioral finance with explainable, real-time AI in decision support. The Shock Score embodies this integration by tying academic models of bias to a machine-readable risk alert. In effect, it operationalizes the “System 1 vs. System 2” idea from [Kahneman (2011)](https://en.wikipedia.org/wiki/Thinking,_Fast_and_Slow) in a portfolio context: when a major news shock (System 1 trigger) approaches, the Shock Score quantifies how much it is likely to activate emotional biases in a given manager or strategy.

In practical terms, the Shock Score addresses the shortcomings identified above. It is a forward-looking indicator (ex-ante) that can be computed continuously as new information flows in. It makes behavioral risk explicit in the same way that traditional risk measures quantify volatility or Value-at-Risk. By doing so, it fills a lacuna in the literature: tying the rich descriptive knowledge of biases to a predictive decision-support tool. In summary, the Shock Score is both novel and relevant: it provides the missing link between theory and practice, operationalizing behavioral finance for real-time portfolio management.

### 3.6.4 Summary of Theoretical and Empirical Contributions

- **Bridging Theory and Practice**: This research formalizes a connection between behavioral finance theory and portfolio decision-making. The proposed Shock Score translates cognitive biases into a quantifiable indicator, thereby meeting the call for tools that integrate psychological insights into investment practice. It operationalizes concepts (e.g. loss aversion, overconfidence) in a way that can be monitored and managed in real time.

- **Novel Methodology**: The thesis introduces a new methodology combining market information (news events, sentiment indicators) with behavioral parameters (bias triggers, stress factors). This fusion of data-driven analytics and psychological modeling has not appeared in prior literature. The Shock Score uses dynamic event inputs to generate forward-looking risk assessments for individual managers, unlike static factor models.

- **Focus on Ex-Ante Adaptation**: By explicitly designing for ex-ante decision support, this work fills a gap in empirical research. It demonstrates how to anticipate and mitigate biases before they impact portfolio decisions. This addresses limitations noted by researchers: existing DSS emphasize quantitative analysis and lack proactive bias alerts, and this thesis’s model directly tackles that issue.

- **Professional Context and Behavioral Integration**: The contributions emphasize application in a realistic context. The Shock Score is intended for use by trained portfolio managers or risk officers, not students. This focus responds to findings (e.g. [Huber et al., 2024](https://www.sciencedirect.com/science/article/abs/pii/S0167268123003324)) that professional behavior differs from lay behavior. Methodologically, it can be calibrated to professional decision-makers (e.g. through empirical studies or surveys), thus enhancing external validity. It models not just market returns but also decision-maker psychology.

- **Advancing Modeling Innovations**: On a theoretical level, the work extends the financial decision-making framework by adding a behavioral “risk factor” to traditional models. Empirically, it suggests new ways to test behavioral theories using real-time events. For example, applying the Shock Score in experiments or simulations can yield data on how specific biases (e.g. anchoring on recent data) propagate into portfolio choices. These contributions enrich both academic theory (by formalizing bias-driven risk modeling) and applied finance (by providing a prototype for next-generation decision support).

Each of these contributions is original to this thesis. By integrating psychology with quantitative finance and by creating an anticipatory risk indicator, the Shock Score advances the literature on decision-making under uncertainty. It provides a concrete example of how behavioral finance can move from explanation to operational support, benefiting both theoretical research and practical portfolio management.


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
