# Hallucination Testing Protocol — Full Citation Audit
**Version:** 1.0  
**Scope:** All 91 references in references.md  
**Purpose:** Verify that every citation in the thesis actually supports the specific claim for which it is cited. This protocol is distinct from the spot-check procedure in `quality_diagnostics_protocol.md` Part 4, which covers 5 citations per chapter. This protocol covers the full reference list.  
**Last updated:** 2026-05-16

---

## WHAT IS A CITATION HALLUCINATION

A citation hallucination occurs when:

1. **Scope mismatch** — the paper addresses the general topic but not the specific claim made in the sentence
2. **Mechanism error** — the paper is cited for a specific mechanism it does not test or propose
3. **Contradiction** — the paper's findings contradict or qualify the claim being made
4. **Wrong paper** — author, year, title, or DOI does not match the cited work
5. **Survey overclaim** — a broad survey paper (e.g., Hirshleifer, 2015; Barberis & Thaler, 2002) is cited as if it originated a specific empirical finding rather than reviewed it
6. **Indirect support** — the paper supports a related but different claim; the thesis overstates the connection

---

## RISK TIERS

References are assigned to three risk tiers based on how they are typically used:

**Tier 1 — High risk (verify first):**
Papers cited for specific empirical mechanisms, specific numerical findings, or papers cited in ways that go beyond their stated scope. Also includes papers added during the April 2026 revision session that introduced new citations not previously verified.

**Tier 2 — Medium risk:**
Papers cited for general theoretical frameworks or survey-level claims. Risk is lower but scope mismatch is still possible.

**Tier 3 — Low risk:**
Papers cited for methodological procedures (PCA, regression, survey design) or well-established definitions (Fama, 1970 for EMH; Sharpe, 1966 for Sharpe ratio). Claim-paper match is typically unambiguous.

---

## VERIFICATION PROCEDURE

For each reference, execute the following steps:

1. **Locate all citations** — search thesis.md for every instance where the reference is cited; record the exact sentence and the claim being made
2. **Fetch the paper** — use the DOI URL from references.md to fetch the abstract and conclusion; for papers with a local file (`file` column populated), the PDF is available at `papers/[filename]`
3. **Assess claim accuracy** — compare the thesis claim against what the abstract/conclusion actually states
4. **Return verdict:**
   - **SUPPORTED** — the paper directly supports the specific claim
   - **PARTIAL** — the paper addresses the general topic; the specific claim is plausible but not explicitly stated
   - **UNSUPPORTED** — the paper does not support the specific claim, contradicts it, or is out of scope
5. **For PARTIAL and UNSUPPORTED:** propose either (a) a replacement citation that does support the claim, or (b) a reframing of the claim to match what the paper actually says

---

## FULL REFERENCE LIST WITH RISK TIER AND VERIFICATION INSTRUCTIONS

### TIER 1 — HIGH RISK

| Reference | DOI / URL | Local file | Verification instruction |
|-----------|-----------|------------|--------------------------|
| Hirshleifer, 2015 | https://doi.org/10.1146/annurev-financial-092214-043752 | ssrn602222.pdf | Cited as "establishing that information shocks influence market prices through behavioral biases." Verify: does the paper specifically address information shocks, or is this overclaimed from a general behavioral finance survey? |
| Loewenstein et al., 2001 | https://doi.org/10.1037/0033-2909.127.2.267 | — | Cited as: affective responses "complement deliberative reasoning" when information shocks occur. Verify: does the paper use "complement" or does it describe affect as competing with / overriding / running parallel to deliberation? The word choice matters. |
| Jolliffe & Cadima, 2016 | https://doi.org/10.1098/rsta.2015.0202 | — | Cited as PCA methodology reference for SC_total construction. Verify: does the paper cover index construction use cases, or only statistical/mathematical theory of PCA? |
| Henderson et al., 2018 | https://doi.org/10.1016/j.jet.2018.10.002 | — | Cited as evidence that "structured pre-commitment mechanisms reduce emotional bias in investment." Verify: does this paper specifically address pre-commitment in investment contexts, or is it a general decision theory paper? |
| Statman, 2019 | https://doi.org/10.2139/ssrn.3668963 | statman2019.pdf | Cited alongside Henderson et al. (2018) for pre-commitment mechanisms reducing emotional bias. Verify: does Statman (2019) make this claim, or is it a broader behavioral finance second-generation survey? |
| Angelova et al., 2023 | https://doi.org/10.3386/w31747 | — | Cited for "limited frameworks or algorithms for adaptive decision support under uncertainty." Verify: does this paper actually identify this gap, or is this an overclaim from its conclusion? |
| Bhandari et al., 2008 | https://doi.org/10.1016/j.dss.2008.07.010 | ssrn219228.pdf | Cited for "decision support systems debiasing investors." Verify: does the paper specifically study debiasing in investment decision-making, or general decision support? |
| Meng et al., 2024 | https://doi.org/10.1016/j.irfa.2024.103219 | — | Cited multiple times as establishing that "information shocks influence market prices through behavioral biases" and for overreaction. Verify: does the paper establish a causal mechanism through behavioral biases specifically, or identify price patterns without behavioral mechanism? |
| Azimi, 2019 | https://doi.org/10.2139/ssrn.3462776 | ssrn3867760.pdf | Cited for "professional context limitation — many behavioral experiments rely on students." Verify: does Azimi (2019) specifically make this methodological critique, or is this a claim about the paper's contribution that overstates it? |
| Barber & Odean, 2001 | https://doi.org/10.1162/003355301556400 | barber2001.pdf | Cited for "overconfident investors trade excessively and earn lower risk-adjusted returns." Verify: does the paper specifically link overconfidence to trading excess and lower returns, or is it a gender study with overconfidence as a secondary mechanism? |
| Neel, 2024 | https://dx.doi.org/10.2139/ssrn.4768248 | ssrn4768248.pdf | Cited for "react more strongly to negative earnings surprises than to positive ones." Verify: this is the disposition effect / loss aversion asymmetry claim — does Neel (2024) specifically test this? |
| Elkind et al., 2022 | https://doi.org/10.3905/JFDS.2021.1.085 | — | Cited for "extreme market conditions trigger panic selling among institutional investors." Verify: does the paper specifically study institutional investors, or retail investors, or both? The claim specifies institutional. |
| Bianchi et al., 2022 | https://dx.doi.org/10.2139/ssrn.3825110 | ssrn5183852.pdf | Cited for "explainability in robo-advisory systems affects investor trust." Verify: does the paper study trust specifically, or delegation, compliance, or other outcomes? |
| Lim, 2025 | http://dx.doi.org/10.1080/15427560.2025.2609644 | ssrn5122748.pdf | Cited as "emotion-aware advisory framework using explainable AI." Verify: does the paper propose and test such a framework, or is it theoretical/conceptual only? |
| Ben-David et al., 2013 | https://doi.org/10.1093/qje/qjt023 | ssrn1364209.pdf | Cited for "managers display overconfidence and miscalibration in their forecasts." Verify: does the paper study portfolio managers specifically, or CFOs / corporate managers? |
| Kahneman & Lovallo, 1993 | https://doi.org/10.1287/mnsc.39.1.17 | kahneman_lovallo1993.pdf | Cited for "professional decision-makers become risk-seeking when performance falls below aspiration." Verify: does this paper make this specific claim, or does it focus on planning fallacy and bold forecasts? |
| Frazzini, 2006 | https://doi.org/10.1111/j.1540-6261.2006.00896.x | ssrn602222.pdf | Cited for disposition effect definition AND ex-ante applicability limitation. Verify: does Frazzini (2006) specifically address ex-ante applicability limitations, or only document the disposition effect empirically? |

---

### TIER 2 — MEDIUM RISK

| Reference | DOI / URL | Local file | Verification instruction |
|-----------|-----------|------------|--------------------------|
| Barberis & Thaler, 2002 | https://dx.doi.org/10.2139/ssrn.327880 | ssrn327880.pdf | Survey paper cited broadly throughout. Verify: for each specific instance, confirm the survey actually covers the specific topic cited (e.g., overconfidence, loss aversion, herding) — survey scope is broad but not unlimited. |
| Kahneman & Tversky, 1979 | https://doi.org/10.2307/1914185 | kahneman1979.pdf | Cited for prospect theory and loss aversion. Verify: standard citation, but also cited for "emotional responses" — confirm the paper addresses affect/emotion or only value function asymmetry. |
| Tversky & Kahneman, 1974 | https://doi.org/10.1126/science.185.4157.1124 | tversky1974.pdf | Cited for availability and representativeness heuristics. Standard citation — verify correct paper (1974 Science paper, not the 1979 Econometrica paper). |
| Kahneman, 2003 | https://doi.org/10.1257/000282803322655392 | kahneman2003.pdf | Cited for bounded rationality and dual-process theory. Verify: does this 2003 AER paper specifically address bounded rationality, or is it primarily about prospect theory and System 1/2? |
| Daniel et al., 1998 | https://doi.org/10.1111/0022-1082.00077 | ssrn3181607.pdf | Cited for overreaction, momentum, and return reversal. Verify: the paper covers overconfidence → overreaction → reversal. Confirm these are the specific mechanisms cited in each thesis sentence. |
| Lo et al., 2005 | https://doi.org/10.1257/000282805774670095 | lo2005.pdf | Cited for "acute stress and arousal impairing decision-making in traders." Verify: does the paper study acute stress specifically, or emotional states more broadly (fear, greed, etc.)? |
| Barber & Odean, 2008 | https://doi.org/10.1093/rfs/hhm079 | barber2008.pdf | Cited for "heightened investor attention and arousal" and overreaction to salient news. Verify: the paper studies attention-driven trading — confirm it specifically addresses arousal/emotional response or only attention/salience. |
| Gervais & Odean, 2001 | https://doi.org/10.1093/rfs/14.1.1 | gervais2001.pdf | Cited for overconfidence among successful traders and excess volatility. Verify: does the paper specifically test excess market volatility, or only individual trader overconfidence? |
| March & Shapira, 1987 | https://doi.org/10.1287/mnsc.33.11.1404 | — | Cited for professional decision-makers becoming risk-seeking below aspiration. Verify: this is the core March & Shapira (1987) behavioral model — confirm the paper is specifically about managerial risk preferences, not general decision theory. |
| Simon, 1955 | https://doi.org/10.2307/1884852 | simon1955.pdf | Cited for bounded rationality and satisficing. Standard citation — verify "satisficing" is actually in this 1955 paper (it is, but confirm). |
| Hodgkinson et al., 1999 | https://onlinelibrary.wiley.com/doi/10.1002/%28SICI%291097-0771(199909)12:3%3C219::AID-BDM320%3E3.0.CO;2-K | — | Cited for "framing shifting risky choices among professional strategists." Verify: does the paper study portfolio managers or strategic decision-makers? The claim specifies professional strategists. |
| Peng & Xiong, 2006 | https://doi.org/10.1016/j.jfineco.2005.05.003 | peng2006.pdf | Cited in opening paragraph for uncertainty and time pressure. Verify: does Peng & Xiong (2006) address time pressure specifically, or only limited attention and category learning? |
| Tetlock, 2007 | https://doi.org/10.1111/j.1540-6261.2007.01232.x | — | Cited for "negative media sentiment predicts temporary market decline consistent with overreaction." Verify: does the 2007 paper make this overreaction claim, or does it focus on sentiment measurement? Note: Tetlock 2005 and Tetlock 2007 are different papers — confirm correct year is used in each citation instance. |
| Tetlock, 2005 | https://dx.doi.org/10.2139/ssrn.685145 | ssrn685145.pdf | Verify correct paper cited in each instance and not confused with Tetlock 2007. |
| Goodell et al., 2023 | https://doi.org/10.1016/j.jbef.2022.100722 | — | Cited for "emotions and stock market anomalies." Verify: this is a systematic review — confirm the specific anomalies or mechanisms cited in the thesis are actually covered in the review. |
| Thaler & Sunstein, 2008 | https://www.worldcat.org/oclc/191578377 | — | Cited for structured decision support reducing emotional reactivity. Verify: Nudge is about libertarian paternalism and choice architecture — confirm the specific application to investment decision-making and emotional reactivity is in the book. |
| Kahneman et al., 2021 | https://hbr.org/2016/10/noise | — | Cited for structured processes reducing inconsistency. Note: URL points to a 2016 HBR article, not the 2021 book "Noise." Verify: is the correct source the 2021 book or the 2016 HBR article? Update URL if needed. |
| Bikhchandani et al., 1992 | https://doi.org/10.1086/261849 | bikhchandani1992.pdf | Cited for herding theory. Standard citation — verify the specific herding mechanism claimed in the thesis (informational cascades) is in this paper. |
| Da et al., 2011 | https://doi.org/10.1111/j.1540-6261.2011.01679.x | da2011.pdf | Cited for investor attention. Standard citation — verify the paper's attention measure (Google SVI) is what is referenced in the SC_total Attention Intensity component. |
| Jiang & Zhu, 2016 | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2891216 | ssrn2891216.pdf | Cited for short-term market underreaction. Verify: the paper is about underreaction — confirm the thesis does not accidentally cite it for overreaction. |
| Löffler et al., 2021 | https://doi.org/10.2139/ssrn.2802570 | ssrn2802570.pdf | Cited for negative news tone and stock market impact. Verify: specific claim cited in thesis matches paper's findings. |
| Song et al., 2015 | https://dx.doi.org/10.2139/ssrn.2631135 | ssrn2631135.pdf | Cited for "sentiment-based signals for automated trading systems." Verify: does the paper explicitly describe the signals as for automated systems only, or is this an interpretation from the thesis? |
| Baker & Wurgler, 2007 | https://doi.org/10.1257/jep.21.2.129 | baker2007.pdf | Cited for investor sentiment index. Verify: Baker & Wurgler 2006 and 2007 are different papers — confirm correct year in each instance and that the specific index described matches. |
| Cremers et al., 2021 | https://doi.org/10.1111/1475-679X.12352 | cremers2021.pdf | Verify claim accuracy for each instance cited. |
| Ben-Rephael et al., 2024 | https://dx.doi.org/10.2139/ssrn.3966758 | ssrn4942370.pdf | Cited for earnings surprises and non-fundamental attention. Verify specific claim accuracy. |
| Wennberg et al., 2016 | https://doi.org/10.1016/j.jbusvent.2016.05.001 | wennberg2016.pdf | Cited for variable risk preferences. Verify claim accuracy. |
| Wiseman & Gomez-Mejia, 1998 | https://doi.org/10.5465/AMR.1998.192967 | wiseman1998.pdf | Cited for behavioral agency model of managerial risk taking. Verify the specific claim made. |
| Lo & Repin, 2002 | https://doi.org/10.1162/089892902317361877 | lo2002.pdf | Cited for psychophysiology of financial risk processing. Verify claim accuracy. |
| Huber et al., 2021 | https://www2.uibk.ac.at/downloads/c9821000/wpaper/2020-11.pdf | — | Cited for market shocks and professional investment behavior. Verify: does the paper study professionals specifically? |
| Huber et al., 2022 | https://doi.org/10.1016/j.jebo.2021.12.007 | huber2022.pdf | Cited for volatility shocks and investment behavior. Verify claim accuracy. |
| Harvey et al., 2025 | https://doi.org/10.2139/ssrn.5122748 | ssrn5122748.pdf | Cited for rebalancing consequences. Verify claim accuracy. |

---

### TIER 3 — LOW RISK

These references are cited for well-established definitions, methodological procedures, or foundational results. Verification is still required but failure probability is low.

| Reference | DOI / URL | Local file | Claim type |
|-----------|-----------|------------|------------|
| Fama, 1970 | https://doi.org/10.1111/j.1540-6261.1970.tb00518.x | — | EMH definition — standard |
| Cochrane, 2005 | https://books.google.com/books/about/Asset_Pricing.html?id=20pmeMaKNwsC | — | Return predictability definition — verify correct edition |
| Sharpe, 1966 | https://doi.org/10.1086/294846 | — | Sharpe ratio definition — standard |
| Sortino & van der Meer, 1991 | https://doi.org/10.3905/jpm.1991.409343 | — | Sortino ratio definition — standard |
| Kahneman, 2011 | https://www.worldcat.org/oclc/706020998 | — | Dual-process theory, System 1/2 — verify specific claims match book content |
| Bergkvist & Rossiter, 2007 | https://doi.org/10.1509/jmkr.44.2.175 | bergkvist2007.pdf | Single-item scale validity — verify claim about unidimensional constructs |
| Krosnick, 1999 | https://doi.org/10.1146/annurev.psych.50.1.537 | — | Survey research methodology — verify specific methodological claim |
| Charness et al., 2012 | https://doi.org/10.1016/j.jebo.2011.08.006 | — | Within-subject vs. between-subject design — standard methodological citation |
| Cameron, Gelbach & Miller, 2011 | https://doi.org/10.1198/jbes.2010.07136 | — | Cluster-robust standard errors — standard econometric citation |
| Petersen, 2009 | https://doi.org/10.1093/rfs/hhn053 | — | Panel data standard errors — standard econometric citation |
| Doronila, 2024 | https://dx.doi.org/10.2139/ssrn.5877342 | — | Likert scale validity in 2024 context — verify the specific claim about single-item scales |
| Jolliffe & Cadima, 2016 | https://doi.org/10.1098/rsta.2015.0202 | — | PCA methodology — note: also Tier 1 above; verify claim carefully |
| Rigobon, 2003 | https://doi.org/10.1162/003465303772815727 | rigobon2003.pdf | Identification through heteroskedasticity — verify specific econometric claim |
| Baruník & Křehlík, 2018 | https://doi.org/10.1093/jjfinec/nby001 | barunik2018.pdf | Frequency dynamics of connectedness — verify specific claim |
| Engelberg & Parsons, 2009 | https://doi.org/10.2139/ssrn.1462416 | ssrn1462416.pdf | Causal impact of media in financial markets — verify claim accuracy |
| Baker et al., 2020 | https://doi.org/10.3386/w983 | baker2020.pdf | COVID uncertainty — verify specific claim |
| Whaley, 2000 | https://doi.org/10.3905/jpm.2000.319728 | whaley2000.pdf | VIX as investor fear gauge — standard citation |
| Lo, 2004 | https://doi.org/10.3905/jpm.2004.442611 | lo2004.pdf | Adaptive markets hypothesis — verify specific claim |
| Rudin, 2019 | https://doi.org/10.1038/s42256-019-0048-x | rudin2019.pdf | Explainability in ML — verify specific claim |
| Jung et al., 2018 | https://doi.org/10.1007/s12599-018-0521-9 | jung2018.pdf | Robo-advisory — verify specific claim |
| Baker & Dellaert, 2018 | https://scholarship.law.upenn.edu/faculty_scholarship/1740/ | — | Robo-advice regulation — verify specific claim |
| Bouvard, 2012 | https://doi.org/10.1093/rfs/hhs068 | bouvard2012.pdf | Real option financing — verify relevance |
| Bianchi et al., 2020 | https://doi.org/10.2139/ssrn.3232721 | ssrn3232721.pdf | Bond risk premia with ML — verify relevance |
| Da, Engelberg & Gao, 2015 | https://doi.org/10.1093/rfs/hhv003 | da2015.pdf | FEARS index — verify specific claim about sentiment |
| Baker & Wurgler, 2006 | https://doi.org/10.1111/j.1540-6261.2006.00885.x | — | Investor sentiment cross-section — verify correct paper vs. 2007 |
| Li, Shah, Noyan & Gao, 2018 | https://doi.org/10.1109/BigData.2018.8621884 | — | News sentiment prediction — verify specific claim |
| Weber, Siebenmorgen & Weber, 2005 | https://psycnet.apa.org/doi/10.1111/j.1539-6924.2005.00627.x | — | Asset risk name recognition — verify specific claim |
| DeMiguel, Garlappi & Uppal, 2009 | https://doi.org/10.1093/rfs/hhm075 | — | Naive diversification — verify specific claim |
| Jiang & Verardo, 2018 | https://doi.org/10.1111/jofi.12699 | — | Herding and skill — verify specific claim |
| Scharfstein & Stein, 1990 | https://www.jstor.org/stable/2006678 | — | Herding and investment — verify specific claim |
| Dasgupta et al., 2011 | https://doi.org/10.1093/rfs/hhq137 | — | Institutional herding price impact — verify specific claim |
| Brown et al., 2014 | https://doi.org/10.1287/mnsc.2013.1751 | — | Analyst recommendations and herding — verify specific claim |
| Coates & Herbert, 2008 | https://doi.org/10.1073/pnas.0704025105 | — | Endogenous steroids and financial risk — verify specific claim |
| Grinblatt & Keloharju, 2001 | https://doi.org/10.1111/0022-1082.00338 | — | What makes investors trade — verify specific claim |
| Chen et al., 2024 | http://doi.org/10.2139/ssrn.4942370 | ssrn4942370.pdf | Professionals and bad luck — verify specific claim |
| RavenPack, 2017 | https://www.ravenpack.com/research/introducing-ravenpack-sentiment-index | — | RavenPack sentiment index — verify this is a legitimate citable source |
| Huang, Roesler & Reske, 2020 | https://doi.org/10.1145/3583780.3615272 | — | FinBERT — verify specific claim and correct DOI (note: year vs. DOI path mismatch — 2020 vs. 2023 conference) |
| SIFMA, 2025 | https://www.sifma.org/research/statistics/fact-book | — | Capital markets fact book — verify the specific statistic cited |
| Swiss Business School, 2025 | [internal document] | C_S_4__Masters_Thesis_Handbook_v_1_8_Ver_1.pdf | Internal handbook — verify any specific requirements cited |

---

## EXECUTION ORDER

Run verification in the following priority order:

1. **All Tier 1 references** — these carry the highest risk of claim mismatch; complete before proceeding
2. **Tier 2 references with no local file** — cannot verify offline; require web_fetch of abstract
3. **Tier 2 references with local file** — can verify from PDF
4. **Tier 3 references** — verify in batch; most will pass without issue

## OUTPUT FORMAT

For each reference verified, report:

```
Reference: [Author, Year]
Claim in thesis: [exact sentence from thesis.md]
Paper says: [what the abstract/conclusion actually states]
Verdict: SUPPORTED / PARTIAL / UNSUPPORTED
Action required: [if PARTIAL or UNSUPPORTED — proposed fix]
```

## KNOWN ISSUES TO RESOLVE FIRST

Before running the full audit, the following are already flagged from prior review sessions:

1. **Kahneman et al., 2021** — URL points to a 2016 HBR article, not the 2021 book "Noise." Verify and update.
2. **Huang, Roesler & Reske, 2020** — DOI path suggests 2023 conference; year mismatch needs resolution.
3. **Loewenstein et al., 2001** — "complement deliberative reasoning" phrasing needs verification against paper's actual framing.
4. **Henderson et al., 2018** — investment pre-commitment context needs verification.
5. **Statman, 2019** — cited for pre-commitment claim; paper is likely a general behavioral finance survey.
