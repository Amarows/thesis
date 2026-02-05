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

The literature review is designed to bridge foundational behavioral finance 
theory with applied challenges in professional investment decision-making, culminating in the rationale for structured 
debiasing tools. 

## 3.1 Link Between Literature and Research Hypotheses

This introductory section defines key theoretical constructs (e.g., information shocks, behavioral bias, Shock Score) 
and explains their relevance to the research problem.

The research hypotheses in this study draw on key concepts from behavioral finance and decision-making literature, 
focusing on how information shocks affect market behavior. An information shock refers to publicly available news or 
updates related to individual stocks that generate a material short-term market reaction, typically observable at 
a daily frequency. Such shocks are characterized by their ability to affect short-term price dynamics and volatility 
without necessarily changing the long-term fundamentals of the underlying firm.

The literature suggests that information shocks influence market prices through behavioral and emotional biases. 
Empirical evidence demonstrates that investors and managers frequently overreact to salient or emotionally charged news 
due to cognitive and affective biases, leading to temporary price distortions rather than rational revaluation based 
on fundamentals.

The Shock Score introduced in this thesis is motivated by existing research on sentiment, attention, 
and volatility-based measures of market reaction. It quantifies the emotional intensity of an information shock 
by capturing abnormal short-term market responses, such as excess daily volatility, that arise from behavioral reactions 
rather than fundamental reassessment.

While the literature contains several indices and measures aimed at capturing market sentiment or uncertainty, 
such as sentiment indices or news-based volatility indicators, there is limited evidence of tools specifically 
designed to support managerial decision-making at the time of an information shock. This gap motivates the development 
and empirical testing of the Shock Score as a decision-support mechanism intended to improve investment decisions by 
reducing behavioral overreaction.

---

## 3.2 Behavioral Biases in Investment Decision-Making

This section surveys behavioral finance theory—how cognitive biases like overconfidence, loss aversion, 
disposition effect, and emotional trading shape investor behavior. It integrates psychological theory and 
empirical findings with a focus on market reactions and volatility.

### 3.2.1 Heuristics and Judgment Under Uncertainty

Professional investors, despite their expertise, are not immune to the cognitive shortcuts and biases that affect human 
judgment under uncertainty. In fact, several prevalent biases – **overconfidence**, **availability and recency bias**, 
**herding**, and **emotional/physiological biases** – can cause even expert decision-makers to react in ways 
that amplify short-term market volatility and lead to overreactions to financial information shocks. 
Below we discuss each of these biases and their impact on short-term market dynamics.

Overconfidence is a well-documented bias wherein individuals exhibit an unwarranted faith in the accuracy of their own 
information and judgment. In finance, overconfident investors consistently overestimate their ability to predict 
outcomes and the precision of their private signals ([Barber & Odean, 2001](https://doi.org/10.1162/003355301556400)). This bias manifests even among 
professionals – for example, successful traders and fund managers can become overconfident in their skill, particularly 
after a streak of good performance ([Gervais & Odean, 2001](https://doi.org/10.1111/0022-1082.00338)). Overconfidence leads investors to underweight risks 
and to trade more aggressively than rational benchmarks would predict, often to their 
own detriment ([Odean, 1999](https://doi.org/10.1093/rfs/12.4.785)). Theoretical models show that overconfident investors introduce **excess volatility** 
into markets by overreacting to new information: prices can jump more than fundamentals justify due to overly aggressive 
trading on one’s private views, creating short-run momentum or “drift” that later corrects ([Daniel et al., 1998](https://doi.org/10.1093/rfs/11.4.921)). 
In essence, overconfidence can cause initial **overreactions** to news (as overconfident traders push prices away 
from equilibrium) followed by subsequent reversals once reality catches up, thus contributing significantly 
to short-term market volatility.

Another class of bias arises from the heuristics investors use to judge the importance of information. 
The **availability heuristic** refers to the tendency to assess the probability or relevance of an event based on how 
easily examples come to mind ([Tversky & Kahneman, 1974](https://www.science.org/doi/10.1126/science.185.4157.1124)). In practice, this means that 
**vivid or recent information** often dominates decision-making because it is readily recalled, even if it is not 
objectively more important. A closely related phenomenon is **recency bias** – the inclination 
to give disproportionately high weight to the most recent events or data points when forming judgments. 
Studies have found that decision-makers (including investors) often overweight recent market events relative 
to earlier information, skewing their expectations ([Hirshleifer, 2020](https://doi.org/10.1146/annurev-financial-012820-025654)). Even seasoned professionals 
are susceptible: for example, mutual fund managers have been shown to extrapolate their fund’s **recent performance** 
into their outlook for the overall market, effectively basing forecasts on the very latest returns rather 
than long-term fundamentals ([Azimi, 2019](https://doi.org/10.1016/j.irfa.2019.101400)). Such availability and recency biases can produce 
**short-term volatility** by fueling overreactions to the news of the day. When a dramatic new information shock occurs, 
investors relying on what is most salient in memory may trade on that news en masse, causing prices to **overshoot** 
(deviating from intrinsic value) before cooler heads prevail. In sum, the dominance of recent, readily-available 
information in professional judgment can lead to exaggerated market moves in the short run, as initial reactions 
are not sufficiently tempered by historical perspective.

Herding describes the tendency of investors to **mimic the actions of others** instead of relying on their own independent analysis. In uncertain environments, even professional investors often follow the crowd – for instance, by buying or selling a stock simply because many of their peers are doing so – assuming that the collective might know better or as a form of career risk management (it may feel safer to err in a crowd than to err alone) ([Scharfstein & Stein, 1990](https://doi.org/10.1086/261653); [Bikhchandani et al., 1992](https://doi.org/10.1086/261849)). In formal terms, *herd behavior occurs when investors follow or copy others’ investment decisions rather than act on their private information*. This bias is prevalent among institutional money managers and analysts, who sometimes converge on the same trades or forecasts (“crowding” into assets), effectively reducing the diversity of opinions in the market. The herding heuristic can severely amplify short-term market movements. When many investors herd into purchasing an asset, their collective action drives the price **above** what fundamentals warrant (and conversely, herd selling drives prices **below** fair value). Empirical research shows that such herding-induced price pressures tend to be short-lived: assets that are aggressively bought by herds often become **temporarily overvalued**, only to experience negative subsequent returns as prices correct, whereas heavily sold assets bounce back with positive future returns once the overreaction abates ([Dasgupta et al., 2011](https://doi.org/10.1093/rfs/hhq068); [Brown et al., 2014](https://doi.org/10.1016/j.jempfin.2013.09.001)). Notably, herding by professional investors (e.g. mutual fund herding) has been directly linked to destabilizing price dynamics, as synchronized trading by large players pushes the market away from equilibrium in the short run. This further underscores how social or institutional pressures to herd can lead to volatility spikes around information events, as many decision-makers move in lockstep rather than counterbalancing each other.

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

---

## 3.3 Managerial Decision-Making Under Uncertainty

Here, the focus shifts to professional investors and managers operating under real-world constraints: 
bounded rationality, organizational pressure, and framing effects. It shows how even experts—despite training—make 
predictably biased decisions under uncertainty.

### 3.3.1 Why Bias Persists Despite Experience

Even seasoned, well-incentivized managers continue to rely on heuristic shortcuts in decisions, underscoring the 
limits of human rationality. **Bounded rationality** – a concept introduced 
by [Simon (1955)](https://doi.org/10.2307/1884852) – posits that people’s cognitive capacity and information access are 
inherently limited, so they **“satisfice”** (seek a good-enough option) rather than optimally solve complex problems. 
In practice, this means that even professional managers with extensive training cannot fully analyze every alternative 
or foresee every outcome. Instead, they fall back on experience-based rules of thumb and intuitive judgments, 
particularly under pressure. These heuristics streamline decision-making but also **embed systematic biases** 
in judgment (e.g. overconfidence, anchoring), which **persist despite expertise**.

High-stakes managerial environments often exacerbate this reliance on heuristics. Real-world portfolio and strategic 
decisions are typically made under **tight time constraints and uncertain information**, making exhaustive rational 
evaluation infeasible. The cognitive effort required to weigh all possible options and outcomes is prohibitive 
when markets move quickly or when a flood of data must be processed in real time. Thus, even **rational, 
incentivized managers resort to mental shortcuts** as a practical response to complexity 
and time pressure (Simon, 1955). This boundedly rational behavior is not due to lack of knowledge or effort, 
but a reflection of **human information-processing limits**. Unfortunately, the very shortcuts that 
make decision-making manageable can systematically skew perceptions of risk and return.

Crucially, research shows that **experience and expertise alone do not eliminate biases**. In a classic study, 
[Hodgkinson et al. (1999)](https://doi.org/10.1177/017084069901900202) found that an MBA-style framing effect 
(i.e. risk choices flipping when a problem was framed in terms of gains vs. losses) affected **senior banking executives 
just as strongly as it did less experienced subjects**. Likewise, 
[Ben-David, Graham, and Harvey (2013)](https://doi.org/10.1093/rfs/hhs068) observed that CFOs and investment 
professionals have **severely miscalibrated forecasts**, displaying narrow confidence intervals and overprecision 
in predicting market returns. [March and Shapira (1987)](https://doi.org/10.1287/mnsc.33.11.1404) also found that most 
managers believed they were *less risk-averse* than their peers and that risks were **largely controllable through skill 
and information**. This hints at overconfidence and an **illusion of control** – biases that do not disappear with greater experience. In short, professional training may raise awareness, but it **does not fully immunize managers against bias** in how they perceive and act on risky decisions.

The persistence of bias is clearly evident in **professional portfolio management** as well. Behavioral finance 
research has documented that even institutional investors and fund managers exhibit many of the same biases as retail investors. For instance, **extrapolation and optimism biases** lead some fund managers to overweight recent winners in their market outlooks and take on excessive risk – a strategy that often backfires with subsequent underperformance ([Baker et al., 2019](https://doi.org/10.1146/annurev-financial-110118-123121)). Similarly, **overconfidence** is common: surveys find that experts routinely overrate their ability to beat the market, and trading data show that biased confidence drives frequent, costly trades ([Barber & Odean, 2001](https://doi.org/10.1162/003355301556400)). Professional decision-makers are also prone to **herding** (following what others are doing) and **loss aversion**, contributing to under-diversified portfolios and suboptimal investment timing ([Statman, 2019](https://doi.org/10.2139/ssrn.3668963)).

In conclusion, **knowing about cognitive biases is not, by itself, enough to guarantee unbiased decisions**. 
Decades of research and practical experience show that **psychological insight must be coupled with structured decision 
support** to truly improve judgment. As [Kahneman et al. (2021)](https://doi.org/10.1257/jep.35.3.36) argue, organizations should *“put systems in place to help”* overcome individual biases by developing formal **rules, processes or decision aids** that keep heuristics in check. In other words, mitigating bias requires more than awareness or good intentions – it demands **systematic support tools and procedures** that guide managers toward more rational choices. This necessity for structured debiasing measures sets the stage for Section 3.4, which will explore how decision-support frameworks can be designed to counteract persistent biases in managerial decision-making.

### 3.3.2 Situational Risk Preferences in Practice

Empirical studies show that professional decision-makers often become **risk-seeking** when performance falls short of 
an aspiration or target. In line with classic “prospect theory” intuition, a fixed target acts as a reference point: when results are below the aspiration level, managers shift into the loss domain and tend to take on more risk to recover ([March & Shapira, 1987](https://doi.org/10.1287/mnsc.33.11.1404)). For example, [Wiseman and Gomez-Mejia (1998)](https://doi.org/10.5465/amr.1998.533225) found that organizations performing poorly “showed increased risk as they neared bankruptcy.” Similarly, [Cooper et al. (2019)](https://doi.org/10.1016/j.jbusvent.2019.04.002) report that entrepreneurs act more risk-averse unless performance falls below their aspiration level, implying that risk-seeking behavior emerges only after missing benchmarks. These findings suggest that framing outcomes relative to a benchmark flips risk preferences, even in the absence of incentives.

Importantly, these biases often **intensify in market downturns**, despite managers’ professional training. Behavioral 
analyses show that sharp declines provoke fear and loss aversion that override logical planning. 
As [Bender et al. (2021)](https://www.msci.com/www/research-paper/behavioral-biases-in/02104602105) note, 
“when markets fall sharply, fear spreads quickly,” and loss aversion “often drives investors to sell at precisely the wrong time.” Controlled experiments confirm this effect: [Graeber and Scheck (2023)](https://doi.org/10.1016/j.jbef.2022.100745) found that during the COVID-19 crash, professional investors reduced risky allocations by 12%, despite unchanged fundamentals. These studies suggest that during downturns, cognitive and emotional pressures amplify the very biases investors are trained to manage.

### 3.3.3 Portfolio-Level Implications

These situational biases often translate into **suboptimal portfolio decisions**. Herding and trend-chasing may creep 
into rebalancing practices. Investors follow crowds into hot sectors or panic-sell during downturns, leading to 
“buying high and selling low” patterns ([Lo & Repin, 2002](https://doi.org/10.2139/ssrn.278181)). 
[Long et al. (2022)](https://doi.org/10.1016/j.jempfin.2022.05.003) warn that panic trading during market stampedes 
leads to premature exits and excessive rotation, undermining long-term diversification. 
Under stress, managers may also **de-risk portfolios too early**, shifting into cash or bonds well before recovery. 
For instance, [Han et al. (2023)](https://doi.org/10.2139/ssrn.4167016) document that managers reduce risk exposure 
by nearly 9% during culturally “unlucky” periods, highlighting how non-financial factors (e.g., superstition, pressure) 
drive allocation errors.

Given the persistence of these effects, researchers emphasize the need for **structured tools and procedures**. 
[Bianchi et al. (2023)](https://doi.org/10.2139/ssrn.4501864) show that automated advice platforms (e.g. robo-advisors) 
help attenuate biases like loss aversion and anchoring. Other work recommends rule-based protocols 
(e.g., fixed-schedule rebalancing or performance-triggered adjustments) as a way to limit emotional interference 
([Statman, 2019](https://doi.org/10.2139/ssrn.3668963)). In summary, structured tools—not intuition alone—are 
required to help even professionals avoid persistent cognitive traps and

---

## 3.4 Tools and Methods to Mitigate Emotional and Behavioral Bias

This section reviews structured interventions, such as decision-support systems, quantitative overlays, and behavioral 
coaching. It presents empirical evidence on how such tools help mitigate bias and improve portfolio performance.

### 3.4.1 Rule-Based Approaches and Pre-Commitment Mechanisms

Many advisors use structured plans and decision rules to curb emotion-driven trading. For example, drafting 
an **Investment Policy Statement (IPS)** that defines goals, risk limits, and rebalancing rules can “put an objective 
framework around portfolio management” and help reduce emotional reactions 
([Statman, 2019](https://doi.org/10.2139/ssrn.3668963)). Pre-commitment devices—like automatic rebalancing schedules, 
stop-loss or profit-taking triggers—shift decisions from being reactive to procedural. Research suggests that “the most 
effective way to reduce emotional reactivity is to commit in advance to specific decision rules,” since these rules are 
followed even when emotions run high 
([Shefrin, 2002](https://books.google.com/books/about/Beyond_Greed_and_Fear.html?id=hX18tBx3VPsC)).

While effective for discipline, these tools rely entirely on consistent human adherence. Their effectiveness diminishes 
under high emotional strain, market crises, or cognitive overload.


### 3.4.2 Automated and AI-Driven Approaches

Beyond static rules, automation can remove human emotion from trading. Robo-advisors and algorithmic systems base 
decisions on data and preset models, “de-humanizing” portfolio reactions and helping investors maintain alignment with 
long-term strategy ([Jung et al., 2018](https://doi.org/10.2139/ssrn.3124820); 
[Baker & Dellaert, 2022](https://doi.org/10.1007/s10603-022-09520-1)). Algorithmic portfolios buy or sell according to 
predefined logic, regardless of investor panic or euphoria.

That said, automated systems have limits. They rely on historical data and user-supplied inputs (e.g. risk preferences), 
which may carry their own biases. Furthermore, they may not adapt well to novel or ambiguous situations. 
To address this, researchers advocate combining automation with human oversight, explainable AI (XAI), and robust audit 
mechanisms ([Bracke et al., 2019](https://www.bankofengland.co.uk/working-paper/2019/explainability-and-its-limits-in-the-uses-of-ai)).

In practice, some firms deploy NLP-based tools to flag potential biases—such as anchoring or herd language—in analyst 
reports or news feeds ([Kazemian et al., 2023](https://doi.org/10.1016/j.jbef.2022.100774)). These alerts serve 
as real-time nudges, but still require expert interpretation.

---

### 3.4.3 Quantifying Bias: Metrics and Behavioral Factor Models

A critical advancement is the quantitative measurement of biases. Recent reviews have identified up to 11 key behavioral 
biases (e.g., disposition effect, overtrading, trend chasing) and 29 empirical proxies to track them in professional 
portfolios ([Duxbury & Summers, 2022](https://doi.org/10.1016/j.jbef.2021.100701)). Common proxies include portfolio 
turnover, concentration ratios, and deviation from benchmark weights.

---

### 3.5 Synthesis and Implications for Portfolio Management
This final section consolidates insights from 3.1 to 3.4, linking behavioral theory and empirical finance with practical investment strategy. It explains how unmanaged bias degrades portfolio quality and why measurement-based tools like the Shock Score may help restore decision efficiency.

Investment professionals, like all decision-makers, face **bounded rationality** and use mental shortcuts when processing complex market information. They cannot evaluate every piece of data fully, so they rely on heuristics and frames to simplify decisions ([Simon, 1955](https://doi.org/10.2307/1884852); [Statman, 2019](https://doi.org/10.2139/ssrn.3668963)). Even experts exhibit systematic biases: for example, portfolio managers can become anchored to initial price levels and overconfident in their forecasts ([Ben-David et al., 2013](https://doi.org/10.1093/rfs/hhs068)). Cognitive framing also distorts judgments—identical information can lead to different choices depending on how it is presented. In sum, these cognitive limits and framing effects cause persistent errors (e.g., home bias, under-diversification, disposition effects) that degrade portfolio performance.

These biases are magnified under **market shocks and stress**. Acute uncertainty impairs deliberative reasoning and shifts managers toward intuition and habit, thereby amplifying heuristics and framing biases ([Lo, 2004](https://doi.org/10.3905/jpm.2004.442611); [Kahneman & Lovallo, 1993](https://doi.org/10.1287/mnsc.39.1.17)). Empirical studies of COVID‑19 and other crises show that investors (including professionals) reacted emotionally to news—overreacting or herding in response to infection or policy announcements ([Baker et al., 2020](https://doi.org/10.1016/j.jfineco.2020.06.013)). The resulting volatility spikes and crowd behavior are well documented. In fact, volatility following an information shock tends to remain elevated for a prolonged period ([Barunik & Kley, 2019](https://doi.org/10.1016/j.jeconom.2019.03.006)), keeping stress high and reinforcing biased reactions. Thus, bounded rationality combined with stress and framing effects produces persistent portfolio errors during shocks.

The implication for portfolio management is that human decision-making alone is often **insufficiently consistent**. Behavioral factor models find that biases like trend-chasing and overtrading measurably harm performance ([Duxbury & Summers, 2022](https://doi.org/10.1016/j.jbef.2021.100701)). Even sophisticated institutions are not immune: analysts and fund managers routinely exhibit overconfidence, loss aversion, and herd behavior ([Ben-David et al., 2013](https://doi.org/10.1093/rfs/hhs068)). Consciously combating bias through training or rules of thumb has limited impact, especially when stress is high. Therefore, modern practice increasingly supplements human judgment with structured tools and algorithms. Advanced dashboards, real-time analytics, and AI models can systematically counteract cognitive limits by surfacing objective signals and alerts ([Statman, 2019](https://doi.org/10.2139/ssrn.3668963); [Bianchi et al., 2023](https://doi.org/10.2139/ssrn.4501864)). For example, AI-driven monitoring systems synthesize market data into clear risk indicators, preventing late or emotional reactions.

In this context, there is a clear need for a quantitative shock indicator. Just as researchers distinguish news-driven “information shocks” from pure volatility shocks ([Rigobon, 2003](https://doi.org/10.1016/S0304-3932(03)00096-6)), a **Shock Score** would quantify the magnitude of new, unexpected information hitting the portfolio. This objective metric could trigger disciplined responses (e.g., reducing leverage or rebalancing according to predefined rules) exactly when managers might otherwise panic or cling to outdated assumptions. Prior work has shown the value of similar constructs—for instance, a “sentiment shock score” has been used to capture extreme news-driven sentiment swings in stock trading ([Engelberg & Parsons, 2011](https://doi.org/10.1111/j.1540-6261.2011.01666.x)). By explicitly measuring shock intensity, the Shock Score aims to improve decision consistency across turbulent markets. In sum, the literature shows that persistent emotional biases and stress-induced errors undermine portfolio choices, motivating automated checks and new tools (like the Shock Score) to guide more stable decisions.



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
