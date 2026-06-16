# Auditable Product-Stable Window Selection for Strong-Motion Records

## Abstract

Strong-motion products depend on the processing interval used to compute peak
motion, waveform energy, and duration-sensitive measures. Fixed windows are
simple to deploy in batch workflows. Their product retention can change
sharply across archives. We evaluate this behavior with 53,463 three-component
records from
InstanceGM and K-NET. Each candidate window is audited by three checks:
retention of full-record peak ground acceleration, retention of relative
waveform energy, and inclusion of the full-record peak time. Fixed 42.00 s
windows show strong dataset dependence. On InstanceGM, feature-onset,
energy-onset, and catalog-P fixed windows have instability rates of 81.25%,
69.91%, and 73.03%. On K-NET, the same windows have instability rates of
4.15%, 3.10%, and 8.25%. We then evaluate a waveform-derived selector that
chooses the shortest candidate passing the product checks and assigns the full
record only when every shorter candidate fails. The selector has 0.84%
full-record fallback overall, with median selected-window durations of 84.94 s
for InstanceGM and 24.66 s for K-NET. The selector recovers 25,468 InstanceGM
feature-onset fixed-window failures and 21,913 InstanceGM energy-onset
fixed-window failures under the same audit. A 5% damping response-spectrum
audit gives overall PSA-retention failure rates of 12.98%, 22.26%, and 32.28%
for feature-onset fixed windows at 0.2 s, 1.0 s, and 3.0 s. The
shortest-stable selector reduces the same rates to 0.02%, 0.87%, and 5.56%
(9, 465, and 2,972 records). Threshold tests show that the 0.95
energy-retention criterion keeps fallback low; a 0.98 criterion raises
overall fallback to 46.84%. The results define a reproducible offline
windowing audit for strong-motion product preparation.

## Plain Language Summary

Strong-motion records need processing windows that keep the shaking used by
engineering and seismological products. A fixed 42.00 s window can lose useful
motion in one archive and include more time than needed in another. We test
windows by checking whether they keep the full-record peak motion, enough
waveform energy, and the time of the full-record peak. A simple offline
selector chooses the shortest candidate window that passes these checks. The
selector gives longer typical windows for InstanceGM and shorter typical
windows for K-NET, with rare full-record fallback at the stated thresholds.

## Introduction

Strong-motion records support earthquake engineering, shaking assessment,
ground-motion model development, and post-event review. Products such as peak
ground acceleration, energy measures, response spectra, and duration-related
metrics depend on the part of the record used during processing. Archive-scale
pipelines often use fixed-duration windows because they are easy to implement
and easy to document. A single fixed interval can miss late product-relevant
motion in one archive and retain unnecessary waveform in another. These
dependencies are a central issue in strong-motion processing and record-quality
work (Douglas, 2003; Boore and Bommer, 2005; Boore et al., 2012).

Fixed windows are also common in public waveform datasets because they make
records uniform, easy to index, and reusable across studies. That practical
value creates a product-quality requirement: the retained interval should be
checked against the strong-motion quantities computed from the record. The
record-level question is whether the selected interval preserves peak motion,
waveform energy, and spectral amplitudes used by downstream users. This study
audits that question directly.

In a production strong-motion workflow, the window is a record-level processing
decision made before product tables are exported. The same interval supports
peak values, response spectra, energy-like measures, duration measures, and
later review of flagged records. A useful selector must keep product-relevant
motion, expose the records that need full-record processing, and leave an audit
trail that can be checked after archive updates. Response spectra and duration
measures are standard engineering products, which makes window retention a
product-level requirement beyond plotting convenience (Trifunac and Brady,
1975; Dobry et al., 1978; Chopra, 2017).

This study treats processing-window selection as a product-retention problem.
Arrival estimates help locate the beginning of shaking. The processing window
must also retain the quantities used downstream. The target output is an
offline record-level window with traceable product checks. This framing matches
strong-motion archive preparation and batch product generation, where the full
record is available before a final processing window is stored.

We use InstanceGM and K-NET to test the same audit on archives with different
product-window behavior. InstanceGM provides a large Italian strong-motion and
seismic waveform archive through the INSTANCE data family (Michelini et al.,
2021; see Data and Resources). K-NET provides Japanese nationwide
strong-motion recordings operated by NIED (Aoi et al., 2004; Okada et al.,
2004; see Data and Resources). Both datasets are evaluated at 100 Hz median
sampling rate, keeping the comparison focused on waveform scale and window
policy. Figure 1 summarizes the workflow.

The paper makes four contributions. First, it defines product stability for
strong-motion processing windows using peak retention, energy retention, and
peak-time inclusion. Second, it quantifies the dataset dependence of common
fixed windows across 53,463 waveform records. Third, it evaluates a
no-catalog, waveform-derived shortest-stable selector with explicit fallback
accounting. Fourth, it reports product-impact recovery, threshold sensitivity,
and response-spectrum retention as auditable engineering-product checks.

## Data

The waveform audit contains 53,463 records with successful feature extraction
(Table 1). InstanceGM contributes 31,344 records from 9,927 events and 568
stations. K-NET contributes 22,119 records from 1,528 events and 921 stations.
The two datasets have a median sampling rate of 100 Hz. InstanceGM records in
the audit have a median duration of 120.00 s. K-NET records have a median
duration of 119.00 s, with a 5th to 95th percentile range from 60 s to 120 s.

Records are grouped into low-magnitude background, M3-M4 small-event, and M4+
strong-motion strata (Table 2). InstanceGM contributes 9,000 low-magnitude
background records, 9,000 M3-M4 records, and 13,344 M4+ records. K-NET
contributes 21 low-magnitude background records, 5,647 M3-M4 records, 15,473
M4+ records, and 978 records with incomplete catalog timing for catalog-P
comparison. The K-NET low-magnitude group is too small for a separate
low-magnitude conclusion. It is retained in the full audit and reported as a
data-availability note.

K-NET waveforms are read from the full converted archive and high-pass filtered
at 1 Hz before feature extraction. This preprocessing matches the earlier
K-NET waveform representation used in the project and separates raw
acceleration offsets from product-window behavior. Strong-motion filtering and
baseline choices can alter downstream amplitudes and spectra, so preprocessing
is kept explicit (Boore, 2001; Douglas and Boore, 2011). Catalog P times
support comparator windows and diagnostics. The main selector uses
waveform-derived candidates.

## Methods

### Waveform Features and Candidate Windows

For each three-component record, we form a vector-amplitude signal from the
standardized component traces. The waveform-derived feature set contains an
effective onset, an energy onset, an energy end, and significant duration.
These features define five candidate window families:

1. Feature-onset fixed: from 2 s before effective onset to 40 s after effective
   onset, yielding a 42.00 s processing interval.
2. Energy-onset fixed: from 2 s before energy onset to 40 s after energy
   onset.
3. Catalog-P fixed: from 2 s before catalog P to 40 s after catalog P. This is
   an arrival-time comparator.
4. Adaptive energy-end: from 2 s before effective onset to 3 s after waveform
   energy end.
5. Full record: the complete record, used as the upper-bound processing
   interval.

The main selector considers feature-onset fixed, energy-onset fixed, and
adaptive energy-end candidates. Catalog-P fixed windows remain in the audit as
arrival-time-based comparators.

### Product-Stability Criteria

Each candidate is evaluated against the full record. Let \(PGA_{\mathrm{full}}\)
and \(E_{\mathrm{full}}\) denote the full-record peak vector amplitude and
vector-signal energy. Let \(PGA_{\mathrm{win}}\) and \(E_{\mathrm{win}}\) denote
the same quantities inside a candidate window. Let \(t_{\mathrm{peak,full}}\)
denote the time of the full-record peak. A candidate is stable when all checks
pass:

\[
\frac{PGA_{\mathrm{win}}}{PGA_{\mathrm{full}}} \geq 0.99,
\quad
\frac{E_{\mathrm{win}}}{E_{\mathrm{full}}} \geq 0.95,
\quad
t_{\mathrm{peak,full}} \in w .
\]

The energy term follows the Arias-style idea of integrating squared motion over
time, applied here as a relative vector-signal energy criterion (Arias, 1970).
The threshold sensitivity analysis repeats the selector with alternative
energy-retention criteria.

### Shortest-Stable Selector

For each record, the selector filters candidate windows by the three
product-stability checks, ranks the stable non-full candidates by duration, and
chooses the shortest one. If the filter yields no stable non-full candidate,
the selector assigns the full record. In compact form,

\[
w^* = \arg\min_{w \in C_{\mathrm{record}}}
\mathrm{duration}(w)
\quad \mathrm{subject\ to}\quad
\mathrm{stable}(w)=1 .
\]

The selected window passes the stated audit by construction. The performance
information comes from fixed-window failure rates, selected duration,
candidate usage, full-record fallback, and product-impact changes relative to
fixed-window baselines.

### Response-Spectrum Retention Audit

We add an independent response-spectrum retention audit to connect processing
windows with engineering strong-motion products. For each selected or fixed
window, we compute 5% damping pseudo-spectral acceleration (PSA) at 0.2 s,
1.0 s, and 3.0 s and compare it with the full-record PSA (Chopra, 2017). A
window has a PSA-retention failure when

\[
\frac{PSA_{\mathrm{win}}(T)}{PSA_{\mathrm{full}}(T)} < 0.95 .
\]

This audit is separate from the selector. The selector uses PGA retention,
relative energy retention, and peak-time inclusion; the response-spectrum
check evaluates whether those selected windows also preserve period-dependent
motion measures.

## Results

### Fixed Windows Are Dataset-Dependent

Fixed 42.00 s windows have different product-retention behavior in the two
datasets (Figure 2; Table 3). InstanceGM fixed-window instability is high:
81.25% for feature-onset fixed windows, 69.91% for energy-onset fixed windows,
and 73.03% for catalog-P fixed windows. K-NET fixed-window instability is much
lower: 4.15%, 3.10%, and 8.25% for the same three windows. Under this audit,
the same fixed duration acts as a dataset-dependent product-window policy.

The adaptive energy-end candidate reduces instability to 1.45% for InstanceGM
and 0.23% for K-NET. It also exposes the scale difference between datasets: the
median adaptive duration is 84.12 s for InstanceGM and 24.66 s for K-NET.

### Magnitude Strata Preserve the Dataset Contrast

The M3-M4 strata show the same dataset contrast (Table 3). In InstanceGM M3-M4
records, feature-onset and energy-onset fixed windows have instability rates of
77.19% and 61.01%. The selector has 1.79% full-record fallback and a median
selected duration of 71.14 s in the same stratum. In K-NET M3-M4 records,
feature-onset and energy-onset fixed windows have instability rates of 1.63%
and 1.61%. The selector has 0.30% fallback and a median selected duration of
19.39 s. The windowing issue follows archive and waveform-scale behavior.
Magnitude strata provide an internal check on that pattern.

### Shortest-Stable Selection Preserves Products with Low Fallback

The shortest-stable selector has 0.84% full-record fallback overall under the
default product-stability criteria (Figure 3; Table 3). Dataset-level fallback
is 1.31% for InstanceGM and 0.18% for K-NET. The full audit contains 451
fallback records, including 412 from InstanceGM and 39 from K-NET. The median
selected duration is 84.94 s for InstanceGM and 24.66 s for K-NET. The selected
windows pass the three product-retention checks by design; fallback and
duration are the operational summaries.

Candidate usage follows the dataset-scale difference. On InstanceGM,
the selector chooses the adaptive energy-end candidate for 84.86% of records
and the energy-onset fixed candidate for 13.52%. On K-NET, it chooses the
adaptive energy-end candidate for 97.26% and the energy-onset fixed candidate
for 2.44%. Full-record fallback occurs for 0.84% of all records.

### Product Impact Relative to Fixed Baselines

The selector changes product retention and window economy relative to fixed
baselines (Figure 4). On InstanceGM, it resolves 25,468
feature-onset fixed-window failures, 21,913 energy-onset fixed-window failures,
and 22,889 catalog-P fixed-window failures under the product-retention audit.
The median energy-retention gain relative to feature-onset fixed windows is
0.347, and the median duration change is 42.94 s. These values indicate that
many InstanceGM fixed windows end before sufficient product-relevant energy is
retained.

K-NET has fewer fixed-window failures. The selector resolves 917
feature-onset fixed-window failures, 686 energy-onset fixed-window failures,
and 847 catalog-P fixed-window failures. The median duration change relative
to feature-onset fixed windows is -17.31 s. The adaptive energy-end candidate
often passes the product-retention checks with a shorter window than the
42.00 s fixed baseline.

### Threshold Sensitivity

The selector is sensitive to the energy-retention criterion (Figure 5). With
\(PGA \geq 0.99\) and \(E \geq 0.95\), the overall full-record fallback
rate is 0.84%. Tightening energy retention to 0.98 raises fallback to 46.84%
overall. InstanceGM fallback increases from 1.31% at 0.95 energy retention to
71.84% at 0.98. K-NET fallback increases from 0.18% to 11.42%. The threshold is
a visible design parameter recorded by the sensitivity analysis.

### Response-Spectrum Retention

The response-spectrum audit strengthens the product-window interpretation
(Figure 6; Table 4). Across all 53,463 records, feature-onset fixed windows
have PSA-retention failure rates of 12.98%, 22.26%, and 32.28% at 0.2 s,
1.0 s, and 3.0 s. The shortest-stable selector reduces the same rates to
0.02%, 0.87%, and 5.56%, corresponding to 9, 465, and 2,972 records.

The 3.0 s period exposes the main residual risk. On InstanceGM, feature-onset
fixed windows have 51.83% PSA-retention failures at 3.0 s, and the selector
has 6.42%. On K-NET, the same comparison is 4.59% and 4.34%. The selector
greatly improves long-period retention for InstanceGM and keeps K-NET losses
low. This result gives the response-spectrum audit a direct engineering role:
short-period and intermediate-period products are nearly preserved under the
selected windows, while long-period PSA remains the product most likely to
expose residual windowing loss. The 3.0 s residual should be reported when
selected windows are used for long-period structural response or soft-site
product checks.

## Discussion

The results support a direct conclusion: strong-motion processing windows
should be evaluated by product retention and window economy. InstanceGM and
K-NET show distinct window scales under a common audit. A fixed 42.00 s window
is too short for many InstanceGM records and longer than needed for many K-NET
records. The product-check selector adapts to that difference and reports its
cost through fallback and selected duration.

The method is easy to audit. Each selected window can be traced to its
candidate type, product-retention values, peak-inclusion status, and fallback
state. This record-level traceability matters for strong-motion product
preparation because processing decisions need to survive later review and
archive updates.

The record-level audit packet connects the aggregate results to practical
review. It includes examples where fixed windows miss late product-relevant
motion and the selector restores retention, examples where K-NET records keep
the product checks with compact windows, and boundary cases assigned to the full
record. These cases let an operator inspect why a record received its processing
window without using hidden labels or manual arrival picks.

The manuscript supports an offline product-window policy. The full record is
available before the processing window is finalized, and each selected window
is evaluated against full-record products. The 0.95 energy-retention criterion
is a design parameter supported by the sensitivity analysis. A stricter 0.98
criterion pushes many InstanceGM records to full-record processing. The
response-spectrum audit adds an engineering-product check and shows that the
selector retains most 0.2-3.0 s PSA values, with the largest residual loss at
3.0 s. The remaining 3.0 s failures identify records that need conservative
handling for long-period spectral products. The selected windows still give a
large product-level gain at 0.2 s, 1.0 s, and most 3.0 s records. Future work
can start from this explicit product-stability baseline and test
group-conditioned thresholds on an external validation archive.

## Conclusions

We evaluated product-stable window selection for 53,463 strong-motion records
from InstanceGM and K-NET. Fixed 42.00 s windows show strong dataset
dependence, with high instability on InstanceGM and much lower instability on
K-NET. The shortest-stable selector uses waveform-derived candidates and
product-retention checks to choose compact processing windows. Under the
default audit, full-record fallback is 0.84% overall, while median selected
duration differs sharply by dataset: 84.94 s for InstanceGM and 24.66 s for
K-NET. The response-spectrum audit shows that overall PSA-retention failures
drop from 32.28% for feature-onset fixed windows to 5.56% for the selected
windows at 3.0 s. The resulting contribution is an auditable offline
product-window policy with explicit thresholds, fallback accounting,
cross-dataset sensitivity, and engineering-product retention checks.

## Data and Resources

Waveforms from the InstanceGM/INSTANCE data family and K-NET were used in this
study. K-NET waveforms were converted with explicit UD -> Z, NS -> N, and
EW -> E component mapping, and K-NET waveform features were computed after
1 Hz high-pass preprocessing. The reproducibility release contains the source
code, focused tests, manifest and worklist files, waveform-feature summaries,
window-stability summaries, selector summaries, product-impact summaries,
threshold-sensitivity summaries, response-spectrum audits, record-level audit
cases, figure sources, checksums, and command log. The public release is
archived at
https://github.com/zhouhaoyiu/strong-motion-product-window-qc/releases/tag/v0.1.0.
InstanceGM/INSTANCE data were accessed through https://doi.org/10.13127/INSTANCE
on 16 June 2026. K-NET/NIED data were accessed through
https://doi.org/10.17598/NIED.0004 on 16 June 2026. Raw waveform archives are
not redistributed and remain subject to provider terms. Code and focused tests
are released under the MIT License; derived summaries, figures, record-audit
plots, manuscript-support metadata, and documentation are released under CC BY
4.0.

An AI-assisted language editing tool was used only to polish manuscript
wording. The authors checked the scientific content, numerical outputs, source
code, figure data, and final manuscript.

## Acknowledgments

The authors thank the data providers of the InstanceGM/INSTANCE data family and
the National Research Institute for Earth Science and Disaster Resilience (NIED)
K-NET program for making waveform data available. This research received no
external funding.

## Declaration of Competing Interests

The authors declare no competing interests.

## Corresponding Author

Correspondence should be addressed to Qiang Ma, Institute of Engineering
Mechanics, China Earthquake Administration, 29 Xuefu Road, Nangang District,
Harbin, Heilongjiang, China; email: maqiang@iem.ac.cn.

## Figure Captions

Figure 1. Workflow for offline product-stable window selection. Each waveform
record is converted into candidate processing windows. Candidate windows are
evaluated by retention of full-record PGA, relative energy, and inclusion of
the full-record peak. The selector chooses the shortest stable non-full
candidate and assigns the full record when no non-full candidate passes the
product-retention checks.

Figure 2. Product-window instability for fixed, adaptive, and selected windows
on InstanceGM and K-NET records. Fixed 42.00 s windows fail frequently on
InstanceGM and less often on K-NET, indicating dataset-dependent product
retention. The shortest-stable selector removes product-retention failures
under the stated audit because it filters candidates by the same criteria.

Figure 3. Selected-window duration and full-record fallback rate for the
shortest-stable selector. The selector chooses longer typical windows for
InstanceGM and shorter typical windows for K-NET. Full-record fallback remains
low at the default PGA-retention and energy-retention criteria.

Figure 4. Product impact relative to fixed-window baselines. The panels show
fixed-window instability, median energy-retention gain, and selected-minus-
baseline duration change for feature-onset, energy-onset, and catalog-P fixed
windows.

Figure 5. Sensitivity of the shortest-stable selector to the energy-retention
criterion with the PGA-retention criterion fixed at 0.99. The default 0.95
energy-retention criterion keeps fallback low. A stricter 0.98 criterion
substantially increases full-record fallback, especially for InstanceGM.

Figure 6. Response-spectrum retention at 5% damping. Panels compare PSA-
retention failure rates at 0.2 s, 1.0 s, and 3.0 s for fixed windows and the
shortest-stable selector. The selected windows reduce overall PSA-retention
failures from 12.98%, 22.26%, and 32.28% for feature-onset fixed windows to
0.02%, 0.87%, and 5.56%.

## Tables

Table 1. Dataset summary.

Table 2. Priority-stratum summary.

Table 3. Product-window stability summary.

Table 4. Response-spectrum retention summary.

## References

Aoi, S., T. Kunugi, and H. Fujiwara (2004). Strong-motion seismograph network
operated by NIED: K-NET and KiK-net, *J. Japan Assoc. Earthq. Eng.* 4, no. 3,
65-74, doi: 10.5610/jaee.4.3_65.

Arias, A. (1970). A measure of earthquake intensity, in *Seismic Design for
Nuclear Power Plants*, R. J. Hansen (Editor), MIT Press, Cambridge,
Massachusetts, 438-483.

Boore, D. M. (2001). Effect of baseline corrections on displacements and
response spectra for several recordings of the 1999 Chi-Chi, Taiwan,
earthquake, *Bull. Seismol. Soc. Am.* 91, no. 5, 1199-1211, doi:
10.1785/0120000703.

Boore, D. M., A. Azari Sisi, and S. Akkar (2012). Using pad-stripped acausally
filtered strong-motion data, *Bull. Seismol. Soc. Am.* 102, no. 2, 751-760,
doi: 10.1785/0120110242.

Boore, D. M., and J. J. Bommer (2005). Processing of strong-motion
accelerograms: needs, options and consequences, *Soil Dyn. Earthq. Eng.* 25,
no. 2, 93-115, doi: 10.1016/j.soildyn.2004.10.007.

Chopra, A. K. (2017). *Dynamics of Structures: Theory and Applications to
Earthquake Engineering*, 5th ed., Pearson, Boston, Massachusetts.

Dobry, R., I. M. Idriss, and E. Ng (1978). Duration characteristics of
horizontal components of strong-motion earthquake records, *Bull. Seismol.
Soc. Am.* 68, no. 5, 1487-1520, doi: 10.1785/BSSA0680051487.

Douglas, J. (2003). What is a poor quality strong-motion record?, *Bull.
Seismol. Soc. Am.* 93, no. 1, 167-184, doi: 10.1785/0120020145.

Douglas, J., and D. M. Boore (2011). High-frequency filtering of strong-motion
records, *Bull. Seismol. Soc. Am.* 101, no. 6, 2873-2885, doi:
10.1785/0120110090.

Michelini, A., S. Cianetti, S. Gaviano, C. Giunchi, D. Jozinovic, and V.
Lauciani (2021). INSTANCE - the Italian seismic dataset for machine learning,
*Earth Syst. Sci. Data* 13, no. 12, 5509-5544, doi:
10.5194/essd-13-5509-2021.

Okada, Y., K. Kasahara, S. Hori, K. Obara, S. Sekiguchi, H. Fujiwara, and A.
Yamamoto (2004). Recent progress of seismic observation networks in Japan:
Hi-net, F-net, K-NET and KiK-net, *Earth Planets Space* 56, no. 8,
xv-xxviii, doi: 10.1186/BF03353076.

Trifunac, M. D., and A. G. Brady (1975). A study on the duration of strong
earthquake ground motion, *Bull. Seismol. Soc. Am.* 65, no. 3, 581-626, doi:
10.1785/BSSA0650030581.
