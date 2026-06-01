# Ideological Polarization in Urban Social Networks
### A Study of Facebook Event Attendance in Copenhagen (2013–2017)

**Christian Cole Turner**  
M.Sc. in Social Data Science — University of Copenhagen, April 2025  
Supervised by Hjalmar Bang Carlsen & David Broomham

**[View the interactive notebook site →](https://christian-c-turner.github.io/Thesis/)**

---

## Abstract

This thesis investigates ideological polarization and homophily in urban social life by analyzing Facebook event co-attendance in Copenhagen from 2013 to 2017. Drawing on a dataset of over 100,000 events and 1 million users, I construct bipartite networks of events and attendees, then project these into event-event and user-user networks. Ideological alignment and demographic traits were previously inferred for politically active users, allowing for the measurement of polarization and social homophily over time and across demographic groups. Using a generalized Euclidean distance measure, I quantify ideological polarization in event networks by event size, revealing increased polarization in the small-events network following the 2015 Danish national election. In user networks, I compare ego-networks to proportional mixing baselines to assess demographic and ideological homophily, focusing on interactions involving ideologically right-leaning users. Results show evidence of ideological homophily, suggesting that even in high-trust, cooperative urban settings like Copenhagen, social life may reflect subtle but meaningful ideological divides.

---

## Research Questions

> **RQ1:** To what extent were Facebook events in Copenhagen ideologically polarized between 2013 and 2017, and how did this fluctuate in relation to the 2015 national election?

> **RQ2:** How do patterns of ideological homophily in Facebook event co-attendance vary among politically active users across demographic groups — particularly Danish men — in the context of rising right-wing nationalism among men across Europe?

---

## Data

The data used in this thesis was originally collected in association with the paper *Mobilizing the Margins — Demographic, Cultural and Political Characteristics of Those Who Mobilize Their Opinion on Social Media* by Lohse et al. (2024). The process of creating the dataset began by gathering a set of local Danish public Facebook pages and recording which users had liked them. From there, snowball sampling was used to collect other pages which these users also liked. This resulted in a dataset of 799,296 events. On the user level, the data contains information on 4.2 million people.

Taking this set of users, ideological scores were inferred following the method of Barberá (2015). Gender classification is based on Danish naming conventions using official legal name registries. The ethnic heritage of users is classified using a fine-tuned BERT language model trained on a subset of 10,000 manually tagged user names, achieving an accuracy of 94.6%.

The ideology scores for users in Copenhagen range from 1.74 to 7.40, with 5.78 as the left-right political divide. Scores are normalised using a custom min-max scaling that places users of opposing ideological extremes at −1 (furthest left) and +1 (furthest right):

$$\hat{s}_i = \begin{cases} \frac{s_i - c}{c - l_{\min}} & \text{if } s_i < c \\ 0 & \text{if } s_i = c \\ \frac{s_i - c}{r_{\max} - c} & \text{if } s_i > c \end{cases}$$

where $s_i$ is the raw ideology score, $c = 5.78$ is the ideological centre, $l_{\min} = 1.74$ and $r_{\max} = 7.40$.

> **Note on data access:** The raw event and user data files are not included in this repository due to size and privacy constraints. The data was provided in association with Lohse et al. (2024) at the University of Copenhagen. Contact the authors or the University of Copenhagen for access enquiries.

---

## Methodology

### Network Construction

Using the datasets of events and users, bipartite networks are constructed for small and medium events over each time period. The bipartite networks consist of event nodes $V_e$ and user nodes $V_u$ connected by edges representing instances of event attendance.

From these, two unipartite projections are created:

- **Event-event network:** Events are connected if they share attendees. Edge weight equals the number of shared attendees between events.
- **User-user network:** Users are connected through event co-attendance. Edge weight equals the total instances of co-attendance between a pair of users.

As required by the Generalized Euclidean measure, only the Largest Connected Component (LCC) of each network is retained. The data is divided into four one-year periods centred on the 2015 election (June 19 – June 18 annually, from 2013 to 2017), and events are split by size: **small** (2–30 attendees) and **medium** (31–100 attendees). Large events (> 100 attendees) are excluded from the analysis.

### Ideological Polarization — Generalized Euclidean Measure

Following Hohmann et al. (2023), the Generalized Euclidean (GE) measure (Coscia, 2020) is applied to quantify structural separation between ideological groups in the event-event networks. The GE measure estimates the overall "effort" required to traverse the network from one group of opinions to another, accounting for both the strength and structure of the connections that link them:

$$\text{GE} = \sqrt{(\mathbf{v}^+ - \mathbf{v}^-)^\top \mathbf{L}^+ (\mathbf{v}^+ - \mathbf{v}^-)}$$

where $\mathbf{L}^+$ is the Moore-Penrose pseudoinverse of the graph Laplacian, and $\mathbf{v}^+$ and $\mathbf{v}^-$ are opinion vectors representing right- and left-leaning event ideology scores. Statistical significance is assessed through a shuffle-based null model (10 shuffles per graph).

### Demographic Mixing — Homophily Measurement

For the user-user networks, homophily is measured by comparing the observed ideological and demographic composition of each user's ego network with expected values derived from overall participation patterns. Deviations represent the nominal percentage-point change in the observed rate of co-attendance relative to the expected values. This analysis is conducted across three demographic dimensions: gender, heritage (Danish/Non-Danish), and political ideology (Left/Right).

---

## Repository Structure

```
.
├── README.md
├── thesis-paper.pdf           ← Full thesis (Turner, 2025)
├── raw-data/                  ← Not committed; place data files here
│   ├── full_data_mod_pickle.csv
│   ├── uid_metadata_segmented.csv
│   └── dk_shape_cleaned.geojson
├── data/processed/            ← Generated by running the notebooks
├── src/
│   ├── backboning.py          ← Noise-corrected backbone algorithm (Coscia, 2020)
│   └── drop_functions.py      ← Iterative event/user filtering utilities
└── notebooks/
    ├── 01_data_cleaning.ipynb
    ├── 02_graph_construction.ipynb
    ├── 03_ideology_analysis.ipynb
    ├── 04_demographic_mixing.ipynb
    ├── 05_supplementary_analysis.ipynb
    └── 06_user_network_stats.ipynb
```

---

## Notebooks

The notebooks must be run **in order**. Each notebook reads from `data/processed/` and writes its outputs back there.

| Notebook | Description | Approx. Runtime |
|---|---|---|
| `01_data_cleaning.ipynb` | Loads raw data; filters events (geographic, date, size); builds user dataset; removes bots; assigns ideology scores; splits into 8 period × size datasets | ~10 min |
| `02_graph_construction.ipynb` | Constructs bipartite graphs; projects to event-event and user-user LCC networks; applies noise-corrected backboning | ~1–2 hrs |
| `03_ideology_analysis.ipynb` | Computes GE distance and null model; produces Figures 7.1–7.2 and Tables 7.1, D.2, D.3 | ~20 min |
| `04_demographic_mixing.ipynb` | Measures homophily by gender, heritage, and ideology; produces Figures 7.3–7.5, E.1–E.3 and Tables E.3–E.5 | ~30 min |
| `05_supplementary_analysis.ipynb` | Subgroup R co-attendance analysis; KDE plots; Appendix A distribution plots; Figure 5.1 | ~30 min |
| `06_user_network_stats.ipynb` | User network basic statistics (Table E.2). **Run interactively** — Louvain community detection on medium networks takes 2–4 hours | 2–4 hrs |

---

## Setup

### Requirements

- Python 3.9+
- `pandas`, `numpy`, `networkx`, `geopandas`, `matplotlib`, `seaborn`, `scipy`, `joblib`

Install dependencies:
```bash
pip install pandas numpy networkx geopandas matplotlib seaborn scipy joblib
```

### Data

Place the following files in `raw-data/` before running the notebooks:

| File | Description |
|---|---|
| `full_data_mod_pickle.csv` | Raw Facebook event data (799,296 events) |
| `uid_metadata_segmented.csv` | Political user metadata (512,154 users) |
| `dk_shape_cleaned.geojson` | Municipality boundaries for Denmark (included) |

The `data/processed/` directory will be populated automatically as you run each notebook.

---

## Key Results

The analysis suggests evidence of ideological polarization within Copenhagen's event-attendance networks, especially among events with 30 people or fewer. These events showed greater internal ideological homogeneity and greater average ideological diversity between events when compared to medium-sized events. These patterns appeared more pronounced after the 2015 election, highlighting a potential connection between national political developments and patterns of social interaction.

Demographic exploration indicates ideological homophily in event co-attendance among politically active users — notably Danish men with right-leaning ideologies. This demographic group appeared to co-attend with other right-leaning users more so than any other group, implying that demographic traits may intersect with ideological preferences in influencing social interaction patterns. Such observations are consistent with broader European trends regarding conservative sentiments among men, suggesting local urban interactions could reflect wider societal shifts.

---

## Ethical Note

The data used in this study was originally collected for academic research purposes and handled in accordance with GDPR. All user identifiers have been hashed prior to this analysis. No attempt has been made to re-identify individuals. The geographic scope (Copenhagen and Frederiksberg municipalities) and the restriction to public Facebook event data limit the risk of privacy exposure.

---

## Citation

If you use this code, please cite the thesis:

```
Turner, Christian Cole (2025). Ideological Polarization in Urban Social Networks:
A Study of Facebook Event Attendance in Copenhagen (2013–2017).
M.Sc. thesis, University of Copenhagen, Faculty of Social Sciences.
```

The data underlying this analysis originates from:

```
Lohse, August, Tobias Priesholm Gårdhus, Snorre Ralund, and Hjalmar Bang Carlsen (2024).
"Mobilizing the Margins — Demographic, Cultural and Political Characteristics of Those Who
Mobilize Their Opinion on Social Media." In: Political Participation, Responsiveness and
Discourse in the Social Media Age. University of Copenhagen, pp. 32–57.
```

The Generalized Euclidean measure is from:

```
Coscia, Michele (2020). "Generalized Euclidean Measure to Estimate Network Distances."
Proceedings of the International AAAI Conference on Web and Social Media 14, pp. 119–129.

Hohmann, Marilena, Karel Devriendt, and Michele Coscia (2023). "Quantifying ideological
polarization on a network using generalized Euclidean distance." Science Advances 9.9, eabq2044.
```
