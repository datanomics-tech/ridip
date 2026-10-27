# Tracks, users and NST2 alignment

RIDIP answers the challenge of each hackathon track with the same platform: one page per sector, one tab per sector in every district profile, and a need score that shows where to act first. Track 3 (Open Innovation) covers four sectors: employment, health, education and transport.

NST2 targets below are as presented by the Government of Rwanda in September 2024 ([Office of the Prime Minister](https://primature.gov.rw/news-detail/prime-minister-presented-to-parliament-governments-five-year-program-nst2); [The New Times](https://www.newtimes.co.rw/article/19487/news/rwanda/unpacking-rwandas-five-year-development-strategy-here-are-the-14-goals/amp)).

## Track 1: Agricultural Productivity

**Challenge:** use data to address real agricultural challenges facing Rwanda.

**Problem.** Productivity depends on farmers using improved seed and fertilizer, protecting soil and getting water to their crops. Use of improved seed ranges from 11% of farmers (Ngororero) to 55% (Nyagatare), and modern irrigation covers about 2% of agricultural land.

**NST2 alignment.** NST2 aims to raise agricultural productivity by more than 50%, expand irrigated land by 85%, improve access to fertilizer and seed, and grow agriculture by over 6% a year.

**Who uses it, for what decision**
- MINAGRI, RAB and district agronomists: which districts to prioritise for seed and fertilizer distribution, irrigation schemes and soil conservation.
- Development partners: where an input or irrigation programme would reach the largest gap.
- Cooperatives and researchers: how a district compares with similar districts (same group).

**Indicators:** improved seeds, inorganic and organic fertilizer, irrigated land, erosion, maize and bean yields (SAS 2025).

## Track 2: Financial Inclusion & Poverty Reduction

**Challenge:** understand financial exclusion, poverty dynamics and the impact of social protection.

**Problem.** Poverty fell from 39.8% to 27.4% between 2017 and 2024, and in every district. But it is still above 40% in six districts, and only 22% of adults are banked, falling to 6% in Nyaruguru. Mobile money has driven formal inclusion to 92%, but access to bank services, smartphones and the internet remains uneven.

**NST2 and Vision 2050 alignment.** Vision 2050 commits Rwanda to eradicating poverty. NST2 targets electricity and clean water for every household by 2029 and fully digital public services, which depend on connectivity.

**Who uses it, for what decision**
- MINECOFIN, LODA and district planners: where poverty reduction and social protection resources are most needed, and whether progress since 2017 is broad-based.
- BNR, AFR and financial service providers: districts with low banking and smartphone access, for outreach and agent networks.
- Civil society: evidence on where households are left behind, with confidence intervals to avoid over-reading small differences.

**Indicators:** poverty (2017 and 2024), banked, formally included, excluded (FinScope 2024), health insurance, smartphone, internet and electricity (EICV7).

## Track 3: Open Innovation

**Challenge:** innovative solutions for national priorities under NST2 and Vision 2050, in any sector (for example health, education, finance or transportation). Finance is covered in Track 2; RIDIP adds four Open Innovation sectors.

### Employment

**Problem.** National youth NEET fell from 34.2% (2017) to 24.5% (2025), but it is still 35.5% in Gisagara. Unemployment ranges from 7% to 18% between districts, and median earnings are three to four times higher in Kigali than in most rural districts.

**NST2 alignment.** NST2 targets at least 1.25 million productive, decent jobs by 2029 (about 250,000 a year).

**Who uses it, for what decision**
- MIFOTRA, the National Employment Programme and districts: where job creation and youth programmes (TVET, apprenticeships, enterprise support) should focus.
- Private investors: where labour is available and under-used.
- Researchers: nine years of district trends (2017–2025) to see which districts are improving.

**Indicators:** unemployment, youth NEET, participation, employment ratio, labour underutilisation (LU4), median earnings (LFS 2017–2025).

### Health

**Problem.** Child stunting is 26.8% nationally (RDHS 2025) but ranges from 8.7% in Nyarugenge to 38.8% in Gicumbi. Coverage of vitamin A, deworming and modern contraception also varies widely.

**NST2 alignment.** NST2 aims to cut stunting from 33% to 15%, quadruple registered health workers and improve maternal, child and infant health services.

**Who uses it, for what decision:** the Ministry of Health, RBC and NCDA, to target nutrition and community-health programmes; district health offices, to compare service coverage with similar districts.

**Indicators:** stunting, modern contraception, birth registration, vitamin A, deworming (RDHS 2025), health insurance (EICV7).

### Education

**Problem.** Primary attendance is high (92.8%), but only 33.7% of secondary-age youth attend secondary school, only 42% of 14–16 year-olds have completed primary school, and computer literacy among 15–24 year-olds is 15.6%.

**NST2 alignment.** NST2 aims to raise pre-primary enrolment from 35% to 65%, train 1 million coders and 500,000 people in advanced ICT, and open TVET Centres of Excellence.

**Who uses it, for what decision:** MINEDUC, REB and districts, to target school-retention, remedial and digital-skills programmes where repetition and drop-out are highest.

**Indicators:** primary and secondary attendance, primary completion, repetition, out-of-school rate, literacy and computer literacy (EICV7, with 2017 comparison for literacy).

### Transport

**Problem.** Almost all households (96%) are within 20 minutes of an all-weather road, but only 27.7% are within 20 minutes of a public transport stage, and a third are an hour or more away.

**NST2 alignment.** Access to roads and public transport connects households to the markets, jobs and services that NST2's agriculture, jobs and health goals depend on.

**Who uses it, for what decision:** MININFRA, RURA and districts, to plan feeder roads, bus routes and stage locations where access is weakest.

**Indicators:** access to all-weather roads and transport stages, bicycle and motorcycle ownership (EICV7).

## How RIDIP addresses the evaluation criteria

| Criterion | How RIDIP addresses it |
| --- | --- |
| Problem understanding & relevance | One clear question per sector, tied to specific NST2 / Vision 2050 targets (above) |
| Data use & methodology | Eight NISR sources, 39 indicators, 2,490 values; every value traceable to its table; standard errors and significance tests; reproducible pipeline and tests ([methodology](methodology.md)) |
| Tech innovation | Explainable need scores, k-means district typology, statistical significance, automated insights, open API and CSV downloads |
| Usability & design | The wireflow journey: Home → Explore → District profile with sector tabs → Compare → Report; search; shareable links; works on phones |
| Tangible impact | Priority districts per sector, district reports for planners and partners, and comparisons that point to similar districts |
