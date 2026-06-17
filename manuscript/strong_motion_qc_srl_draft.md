# Auditable Processing-Window Quality Control for Strong-Motion Products

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
record only when every shorter candidate fails. Only 0.84% of records are
assigned to full-record processing, with median selected-window durations of
84.94 s for InstanceGM and 24.66 s for K-NET. The selector recovers 25,468 InstanceGM
feature-onset fixed-window failures and 21,913 InstanceGM energy-onset
fixed-window failures under the same audit. A 5% damping response-spectrum
audit gives overall PSA-retention failure rates of 12.98%, 22.26%, and 32.28%
for feature-onset fixed windows at 0.2 s, 1.0 s, and 3.0 s. The
shortest-stable selector reduces the same rates to 0.02%, 0.87%, and 5.56%
(9, 465, and 2,972 records). Threshold tests make the operating trade-off
explicit: the 0.95 energy-retention criterion keeps full-record assignment
rare, whereas a 0.98 criterion raises the overall assignment rate to 46.84%.
An external PNWAccelerometers check and a production-style routing case test
how the same audit transfers to a third archive and to batch product
preparation. The results define a reproducible offline quality-control workflow
for strong-motion product windows.

## Plain Language Summary

Strong-motion records need processing windows that keep the shaking used by
engineering and seismological products. A fixed 42.00 s window can lose useful
motion in one archive and include more time than needed in another. We test
windows by checking whether they keep the full-record peak motion, enough
waveform energy, and the time of the full-record peak. A simple offline
selector chooses the shortest candidate window that passes these checks. The
selector gives longer typical windows for InstanceGM and shorter typical
windows for K-NET, with rare full-record assignment at the stated thresholds.

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

Operational systems and services already cover many surrounding parts of the
strong-motion processing problem. PRISM combines batch processing with a review
interface for strong-motion records (Jones et al., 2017). The USGS gmprocess
workflow supports rapid automated ground-motion processing (Thompson et
al., 2025). European RRSM and ESM services provide rapid raw strong-motion
parameters and reviewed engineering strong-motion products (Cauzzi et al., 2016;
Luzi et al., 2016). Recent deep-learning work estimates P arrival time and
high-pass corner frequency for strong-motion displacement processing (Inocente
and Maruyama, 2026), and national product systems calculate PGA, PGV, PGD,
intensity, duration, Fourier spectra, response spectra, and related outputs
(Liu et al., 2025). This study isolates the record-level processing-window
duration used to retain product-relevant motion before those products are
reported.

Fixed windows are also common in public waveform datasets because they make
records uniform, easy to index, and reusable across studies. That practical
value creates a product-quality requirement: the retained interval needs to be
checked against the strong-motion quantities computed from the record. The
record-level question is whether the selected interval preserves peak motion,
waveform energy, and spectral amplitudes used by downstream users. This study
audits that question directly.

In a production strong-motion workflow, the window is a record-level processing
decision made before product tables are exported. The same interval supports
peak values, response spectra, energy-like measures, duration measures, and
later review of flagged records. A useful selector keeps product-relevant
motion, exposes the records that need full-record processing, and leaves an audit
trail that can be checked after archive updates. Response spectra and duration
measures are standard engineering products, which makes window retention a
product-level requirement beyond plotting convenience (Trifunac and Brady,
1975; Dobry et al., 1978; Chopra, 2017).

This study treats processing-window choice as a product-retention quality-control problem.
Arrival estimates help locate the beginning of shaking. The processing window
also retains the quantities used downstream. The target output is an
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

The paper contributes a quality-control workflow for strong-motion product
windows. It defines product-stability checks using peak retention, energy
retention, and peak-time inclusion; quantifies fixed-window dataset dependence
across 53,463 waveform records; evaluates a no-catalog shortest-stable rule
with explicit full-record accounting; and reports product-impact recovery,
threshold sensitivity, response-spectrum retention, an external PNW audit, and
a production-routing case.

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

We add PNWAccelerometers as a third-party external check after the primary
InstanceGM/K-NET audit (Ni et al., 2023; see Data and Resources). The local
SeisBench cache contains 6,107 three-component accelerometer records with
catalog P/S samples. Median record duration is 150.01 s and median magnitude is
1.83. This dataset is reported separately because its event and archive
mechanism differ from the primary 53,463-record denominator.

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
candidate usage, full-record assignment, and product-impact changes relative to
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
77.19% and 61.01%. The selector assigns 1.79% of records to the full interval and has a median
selected duration of 71.14 s in the same stratum. In K-NET M3-M4 records,
feature-onset and energy-onset fixed windows have instability rates of 1.63%
and 1.61%. The selector assigns 0.30% of records to the full interval and has a median selected duration of
19.39 s. The windowing issue follows archive and waveform-scale behavior.
Magnitude strata provide an internal check on that pattern.

### Shortest-Stable Selection Preserves Products with Limited Full-Record Assignment

The shortest-stable selector assigns 0.84% of records to full-record
processing under the default product-stability criteria (Figure 3; Table 3).
Dataset-level full-record assignment is 1.31% for InstanceGM and 0.18% for
K-NET. The full audit contains 451 records assigned to the full interval,
including 412 from InstanceGM and 39 from K-NET. The median selected duration
is 84.94 s for InstanceGM and 24.66 s for K-NET. The selected windows pass the
three product-retention checks by design; assignment rate and duration
summarize the operating cost.

Candidate usage follows the dataset-scale difference. On InstanceGM,
the selector chooses the adaptive energy-end candidate for 84.86% of records
and the energy-onset fixed candidate for 13.52%. On K-NET, it chooses the
adaptive energy-end candidate for 97.26% and the energy-onset fixed candidate
for 2.44%. Full-record assignment occurs for 0.84% of all records.

### Product Impact Relative to Fixed Baselines

The selector changes product retention and selected-window length relative to fixed
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
\(PGA \geq 0.99\) and \(E \geq 0.95\), the overall full-record assignment
rate is 0.84%. Tightening energy retention to 0.98 raises the rate to 46.84%
overall. InstanceGM full-record assignment increases from 1.31% at 0.95 energy
retention to 71.84% at 0.98. K-NET assignment increases from 0.18% to 11.42%.
The sensitivity analysis makes this trade-off explicit: stricter energy
retention yields a more conservative selector and substantially more
full-record assignments.

### Response-Spectrum Retention

The response-spectrum audit strengthens the product-window interpretation
(Figure 6; Table 4). Across all 53,463 records, feature-onset fixed windows
have PSA-retention failure rates of 12.98%, 22.26%, and 32.28% at 0.2 s,
1.0 s, and 3.0 s. The shortest-stable selector reduces the same rates to
0.02%, 0.87%, and 5.56%, corresponding to 9, 465, and 2,972 records.

The 3.0 s period exposes the main residual risk. On InstanceGM, feature-onset
fixed windows have 51.83% PSA-retention failures at 3.0 s, and the selector
has 6.42%. On K-NET, the same comparison is 4.59% and 4.34%. The selector
substantially improves long-period retention for InstanceGM without increasing
K-NET losses. This result clarifies the engineering relevance of the spectrum
audit: short-period and intermediate-period products are largely preserved
under the selected windows, while long-period PSA remains the product most
likely to expose residual windowing loss. Records failing the 3.0 s PSA
threshold are listed in the record-level audit material for long-period
structural-response or soft-site product review.

### External PNWAccelerometers Check

The PNWAccelerometers audit shows how the same criteria behave on a third
public strong-motion archive. Fixed 42.00 s windows are a poor match for this
cache: feature-onset, energy-onset, and catalog-P fixed windows fail the
product-stability audit for 91.99%, 91.88%, and 90.34% of 6,107 records. The
shortest-stable selector assigns 10.58% of records to full-record processing
and selects a median duration of 142.93 s. Most accepted non-full records use
the adaptive energy-end candidate.

The response-spectrum audit gives the same operational message. For
feature-onset fixed windows, PNW PSA-retention failures are 82.72%, 45.67%, and
42.31% at 0.2 s, 1.0 s, and 3.0 s. The shortest-stable selector reduces those
rates to 0.02%, 3.59%, and 9.53%. The PNW result is reported outside the
primary denominator and exposes an external archive that needs long windows or
full-record processing for product-stable output.

### Product-Production Routing Case

We combine the primary audit and the PNW external check into a production-style
routing table. Each record is routed to one of three actions: selected-window
acceptance, full-record processing, or long-period PSA review. The review route
is triggered when the selected window passes the PGA, energy, and peak-time
checks but fails the 3.0 s PSA-retention audit.

Across 59,570 records, 54,919 records (92.19%) route to direct selected-window
acceptance, 1,097 records (1.84%) route to full-record processing, and 3,554
records (5.97%) route to long-period PSA review. The dataset split clarifies
the workload source: PNWAccelerometers contributes 646 of the 1,097 full-record
routes and 582 of the 3,554 long-period PSA review routes. This table is a
reproducible product-preparation worklist. It is not a measured human-review
time study.

## Discussion

The results show that strong-motion processing windows need product-retention
checks together with selected-window length. InstanceGM and K-NET show distinct
window scales under a common audit. A fixed 42.00 s window is too short for many
InstanceGM records and longer than needed for many K-NET records. The
product-check selector adapts to that difference, and its operating cost is
summarized by full-record assignment and selected duration.

The dominant failure mechanism is energy truncation. In InstanceGM, all 25,468
feature-onset fixed-window failures have energy-retention loss under the audit,
and 8,504 also lose PGA. In K-NET, 916 of 917 feature-onset fixed-window
failures have energy-retention loss, and 25 have PGA loss. The same 42.00 s
interval interacts with archive-specific waveform duration and tail
energy. This mechanism explains why a single fixed duration transfers poorly
between archives even when both datasets are sampled at 100 Hz and processed by
the same product-retention criteria.

The quality-control workflow leaves a clear audit trail. Each selected window can be traced to its
candidate type, product-retention values, peak-inclusion status, and
full-record assignment state. This record-level traceability matters for strong-motion product
preparation because processing decisions need to survive later review and
archive updates.

The record-level audit packet connects the aggregate results to practical
review. It includes examples where fixed windows miss late product-relevant
motion and the selector restores retention, examples where K-NET records keep
the product checks with compact windows, and boundary cases assigned to the full
record. These cases let an operator inspect why a record received its processing
window without using hidden labels or manual arrival picks.

These results support an offline product-window policy. The full record is
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
group-conditioned thresholds for archives whose external audit resembles the
PNWAccelerometers long-window case.

## Conclusions

We evaluated product-stable window selection for 53,463 strong-motion records
from InstanceGM and K-NET. Fixed 42.00 s windows show strong dataset
dependence, with high instability on InstanceGM and much lower instability on
K-NET. The shortest-stable selector uses waveform-derived candidates and
product-retention checks to choose compact processing windows. Under the
default audit, full-record assignment is 0.84% overall, while median selected
duration differs sharply by dataset: 84.94 s for InstanceGM and 24.66 s for
K-NET. The response-spectrum audit shows that overall PSA-retention failures
drop from 32.28% for feature-onset fixed windows to 5.56% for the selected
windows at 3.0 s. The resulting contribution is an auditable offline
product-window quality-control workflow with explicit thresholds, full-record
assignment accounting, cross-dataset sensitivity, and engineering-product
retention checks.

An external PNWAccelerometers audit adds 6,107 third-party records as a stress
check. It shows high fixed-window failure and a median selected-window duration
of 142.93 s, confirming that external archive mechanism must be audited before
fixed windows are reused. A production-routing case over 59,570 records
separates direct selected-window acceptance, full-record processing, and
long-period PSA review, giving a practical template for batch product
preparation.

## Data and Resources

Waveforms from the InstanceGM/INSTANCE data family and K-NET were used for the
primary audit. PNWAccelerometers was used as a third-party external check.
K-NET waveforms were converted with explicit UD -> Z, NS -> N, and EW -> E
component mapping, and K-NET waveform features were computed after 1 Hz
high-pass preprocessing. The reproducibility release contains the source code,
focused tests, manifest and worklist files, waveform-feature summaries,
window-stability summaries, selector summaries, product-impact summaries,
threshold-sensitivity summaries, response-spectrum audits, PNW external-audit
summaries, production-routing outputs, record-level audit cases, figure
sources, checksums, and command log. The public release is
archived at
https://github.com/zhouhaoyiu/strong-motion-product-window-qc/releases/tag/v0.1.0.
InstanceGM/INSTANCE data were accessed through https://doi.org/10.13127/INSTANCE
on 16 June 2026. K-NET/NIED data were accessed through
https://doi.org/10.17598/NIED.0004 on 16 June 2026. PNWAccelerometers was
accessed through the local SeisBench cache on 18 June 2026 and follows Ni et
al. (2023), https://doi.org/10.26443/seismica.v2i1.368. Raw waveform archives
are not redistributed and remain subject to provider terms. Code and focused
tests are released under the MIT License; derived summaries, figures,
record-audit plots, manuscript-support metadata, and documentation are released
under CC BY 4.0.

An AI-assisted language editing tool was used only to polish manuscript
wording. The authors checked the scientific content, numerical outputs, source
code, figure data, and final manuscript.

## Acknowledgments

The authors thank the data providers of the InstanceGM/INSTANCE data family,
the National Research Institute for Earth Science and Disaster Resilience
(NIED) K-NET program, and the PNWAccelerometers/SeisBench data contributors for
making waveform data available. This research received no external funding.

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

Figure 3. Selected-window duration and full-record assignment rate for the
shortest-stable selector. The selector chooses longer typical windows for
InstanceGM and shorter typical windows for K-NET. Only a small fraction of
records are assigned to the full interval under the default PGA-retention and
energy-retention criteria.

Figure 4. Product impact relative to fixed-window baselines. The panels show
fixed-window instability, median energy-retention gain, and selected-minus-
baseline duration change for feature-onset, energy-onset, and catalog-P fixed
windows.

Figure 5. Sensitivity of the shortest-stable selector to the energy-retention
criterion with the PGA-retention criterion fixed at 0.99. The default 0.95
energy-retention criterion keeps full-record assignment rare. A stricter 0.98
criterion substantially increases full-record assignment, especially for
InstanceGM.

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

Cauzzi, C., R. Sleeman, J. Clinton, J. D. Ballesta, O. Galanis, and P. Kastli
(2016). Introducing the European Rapid Raw Strong-Motion database, *Seismol.
Res. Lett.* 87, no. 4, 977-986, doi: 10.1785/0220150271.

Dobry, R., I. M. Idriss, and E. Ng (1978). Duration characteristics of
horizontal components of strong-motion earthquake records, *Bull. Seismol.
Soc. Am.* 68, no. 5, 1487-1520, doi: 10.1785/BSSA0680051487.

Douglas, J. (2003). What is a poor quality strong-motion record?, *Bull.
Seismol. Soc. Am.* 93, no. 1, 167-184, doi: 10.1785/0120020145.

Douglas, J., and D. M. Boore (2011). High-frequency filtering of strong-motion
records, *Bull. Seismol. Soc. Am.* 101, no. 6, 2873-2885, doi:
10.1785/0120110090.

Inocente, I., and Y. Maruyama (2026). Automated strong-motion record
processing via deep learning-based simultaneous P-wave identification and
high-pass corner-frequency selection, *Seism. Rec.* 6, no. 2, 219-229, doi:
10.1785/0320260007.

Jones, J. M., E. Kalkan, C. D. Stephens, and P. Ng (2017). PRISM Software:
Processing and Review Interface for Strong-Motion Data, *Seismol. Res. Lett.*
88, no. 3, 851-866, doi: 10.1785/0220160200.

Liu, Y., L. Zou, Q. Zhang, and X. Li (2025). Strong-Motion Data Processing and
Product Generation System for Earthquake Early Warning Network, *Appl. Syst.
Innov.* 8, no. 6, 172, doi: 10.3390/asi8060172.

Luzi, L., R. Puglia, E. Russo, M. D'Amico, C. Felicetta, F. Pacor, G. Lanzano,
U. Ceken, J. Clinton, G. Costa, L. Duni, E. Farzanegan, P. Gueguen, C.
Ionescu, I. Kalogeras, et al. (2016). The Engineering Strong-Motion
Database: A platform to access pan-European accelerometric data, *Seismol.
Res. Lett.* 87, no. 4, 987-997, doi: 10.1785/0220150278.

Michelini, A., S. Cianetti, S. Gaviano, C. Giunchi, D. Jozinovic, and V.
Lauciani (2021). INSTANCE - the Italian seismic dataset for machine learning,
*Earth Syst. Sci. Data* 13, no. 12, 5509-5544, doi:
10.5194/essd-13-5509-2021.

Ni, Y., A. Hutko, F. Skene, M. Denolle, S. Malone, P. Bodin, R. Hartog, and A.
Wright (2023). Curated Pacific Northwest AI-ready Seismic Dataset, *Seismica*
2, no. 1, doi: 10.26443/seismica.v2i1.368.

Okada, Y., K. Kasahara, S. Hori, K. Obara, S. Sekiguchi, H. Fujiwara, and A.
Yamamoto (2004). Recent progress of seismic observation networks in Japan:
Hi-net, F-net, K-NET and KiK-net, *Earth Planets Space* 56, no. 8,
xv-xxviii, doi: 10.1186/BF03353076.

Trifunac, M. D., and A. G. Brady (1975). A study on the duration of strong
earthquake ground motion, *Bull. Seismol. Soc. Am.* 65, no. 3, 581-626, doi:
10.1785/BSSA0650030581.

Thompson, E. M., M. Hearne, B. T. Aagaard, J. M. Rekoske, C. B. Worden, M. P.
Moschetti, H. E. Hunsinger, G. C. Ferragut, G. A. Parker, J. A. Smith, K. K.
Smith, and A. R. Kottke (2025). Automated, near real-time ground-motion
processing at the U.S. Geological Survey, *Seismol. Res. Lett.* 96, no. 1,
538-553, doi: 10.1785/0220240021.
