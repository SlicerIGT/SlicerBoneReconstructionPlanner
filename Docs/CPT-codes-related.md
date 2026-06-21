# Coding & Reimbursement Notes (U.S. CPT®)

## TL;DR

- Virtual surgical planning is related to `1032T` (`+1033T`)
- 3D printed anatomical models are related to `0559T` (`+0560T`)
- 3D printed anatomic guides are related to `0561T` (`+0562T`)

> ## ⚠️ No warranty — not advice — no liability
>
> This document is provided **"as is", without warranty of any kind**, express or
> implied, including but not limited to warranties of accuracy, completeness,
> merchantability, or fitness for a particular purpose.
>
> It is **not** medical advice, legal advice, billing or coding advice, financial
> advice, regulatory guidance, educational/instructional material, or any form of
> professional advice. It does **not** establish, confirm, or guarantee that any
> service is covered, billable, or payable by any payer, and it does **not** create
> a coding, billing, or compliance recommendation of any kind.
>
> Code numbers, descriptors, bundling rules, effective dates, and payer policies
> change and vary by jurisdiction, payer, and contract. **You are solely
> responsible** for verifying any code, rule, or amount with the current official
> **AMA CPT®** materials, your payer(s), and your own qualified, licensed
> professionals (e.g., a certified medical coder, compliance officer, and legal
> counsel) before relying on anything here.
>
> Any use of, or reliance on, this document is **entirely at your own risk**.
> Using or following it creates **no obligation, duty, or liability** for the
> author(s), maintainer(s), or contributor(s) of BoneReconstructionPlanner, who
> disclaim all liability to the fullest extent permitted by law. This document is
> independent of, and adds nothing to, the warranty and liability terms of the
> software, which remain governed solely by the project's BSD-3-Clause `LICENSE`.

---

## Why this file exists

BoneReconstructionPlanner (BRP) is a free, open-source 3D Slicer extension for
virtual surgical planning (VSP) of mandibular reconstruction with a fibula free
flap, and for generating patient-specific cutting guides. Users in the United
States sometimes ask which CPT® codes *relate to* this kind of workflow. The
codes below are listed for orientation only, with the disclaimer above applying
in full. Nothing here is unique to BRP; the same families apply to any
software-based 3D planning and/or in-house 3D printing workflow.

> **Scope:** CPT® is a U.S. code set. It is generally irrelevant outside the U.S.
> billing context. CPT® is a registered trademark of the American Medical
> Association (AMA); the codes and their official descriptors are owned and
> copyrighted by the AMA. Reproducing AMA descriptors, or using CPT® in a product,
> may require a license from the AMA. The descriptions below are **paraphrased in
> plain language**, not official descriptors.

---

## How a BRP-style workflow maps to coding concepts

A typical end-to-end workflow touches several distinct concepts, and U.S. coding
treats them separately:

1. **Image rendering / 3D reconstruction** of the CT (creating viewable 3D from
   tomographic slices).
2. **Digital 3D modeling and virtual surgical planning** done in software — i.e.,
   what BRP itself does: building patient-specific bone surface models, moving cut
   planes, virtually "trialing" osteotomies, and digitally designing the guides.
3. **Physical 3D printing of a cutting/drilling guide** (the fibula guide and the
   mandible guide exported as STL and printed).
4. **Physical 3D printing of an anatomic model** (e.g., a printed neomandible used
   to pre-bend a reconstruction plate).

Each concept maps to a different code family below.

---

## Code families

### A. Software-based / digital 3D planning — **1030T–1035T** *(new)*

Six **Category III** codes effective **July 1, 2026** (revised guidelines and
parenthetical notes released by the AMA on December 30, 2025; published in CPT®
2027). These were created specifically to describe **software-based 3D surface
modeling and digital surgical simulation** — i.e., planning workflows that do
**not** necessarily involve any physical 3D printing. This is the family most
directly aligned with what BRP does as a *digital* VSP tool.

The set is structured as three "first / each-additional" pairs (odd = first
component; the even add-on = each additional component):

| Code | Add-on? | Paraphrased meaning |
| --- | --- | --- |
| `1030T` | first | Create a patient-specific digital 3D surface-mesh model — **no** subsequent digital simulation and **no** computational analysis. |
| `+1031T` | add-on | Each additional such digital 3D surface model. |
| `1032T` | first | Create a patient-specific digital 3D model **and** use it for a **digital simulation**. |
| `+1033T` | add-on | Each additional digital 3D model used for a digital simulation. |
| `1034T` | first | Create a digital 3D model, use it for a digital simulation, **and** perform **computational analyses**. |
| `+1035T` | add-on | Each additional, including the computational-analysis work. |

Per the AMA notes, a "digital simulation" can include things like iteratively
designing digital intra-procedural templates/guides, virtually "trialing"
different implants/designs/surgical approaches, or virtual contingency planning
for potential complications — and may encompass VR/XR-based planning.

### B. Physical 3D-printed models & guides — **0559T–0562T**

Four **Category III** codes effective **July 1, 2019**, for the **physical**
3D-printed output:

| Code | Add-on? | Paraphrased meaning |
| --- | --- | --- |
| `0559T` | first | First individually prepared/processed component of a **3D-printed anatomic model** from the image data set(s). |
| `+0560T` | add-on | Each additional printed component of the model (use with `0559T`). |
| `0561T` | first | First **3D-printed anatomic guide** (e.g., a cutting/drilling guide) designed from the image data set(s). |
| `+0562T` | add-on | Each additional printed guide (use with `0561T`). |

In BRP terms: a printed **neomandible model** points at `0559T`/`+0560T`; the
printed **fibula and mandible cutting guides** point at `0561T`/`+0562T`.

---

## "Do not report together" / pairing rules *(paraphrased)*

- **Printed model vs. rendering/digital:** `0559T`/`0560T` should not be reported
  together with `1030T–1035T`.
- **Digital-then-printed (unaltered):** if a model was reported under
  `1030T–1035T` and is later 3D-printed **without being altered in the interim**,
  the 3D-printing codes (`0559T`–`0562T`) are reported with **modifier 52**
  (reduced services).
- **Add-on codes** (`+0560T`, `+0562T`, `+1031T`, `+1033T`, `+1035T`) are reported
  only in addition to their corresponding primary code, never alone.

---

## Reality check on Category III codes

- Category III codes (the `…T` codes: `1030T–1035T` and `0559T–0562T`) are
  **temporary tracking codes for emerging technology**, used to gather utilization
  and outcomes data.
- They are typically **carrier-priced and frequently reimbursed at $0** — payment
  is at each payer's discretion and **is not guaranteed**. Their existence does
  not imply coverage.

---

> ### Reminder
> Everything above is paraphrased, time-sensitive, U.S.-specific orientation
> material provided **without warranty** and **is not** medical, legal, billing,
> coding, or other professional advice, and **is not** educational/instructional
> material. Confirm all codes, rules, dates, and payment with the official AMA
> CPT® source, your payer(s), and your own qualified professionals. Reliance is at
> your own risk and imposes **no liability** on the BoneReconstructionPlanner
> author(s), maintainer(s), or contributor(s).
>
> *CPT® is a registered trademark of the American Medical Association.*
