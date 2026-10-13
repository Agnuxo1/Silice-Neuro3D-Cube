# Candidate laboratory partners: fs-written waveguides in silica (Silice-Neuro3D-Cube)

## Resumen en español

1. Se evaluaron 23 candidatos (A: 11, B: 4, C: 8), ordenados por ajuste 1-5; ninguno llega a 5, porque ninguno documenta a la vez guías de trinchera en sílice o borosilicato a 1550 nm, una vía abierta a usuarios externos y metrología cut-back.
2. Los cinco primeros: ALF-USAL (España, contratos de I+D, revestimiento deprimido), Politecnico di Milano/CNR-IFN (mallas con calentadores a 1550 nm), EPFL Galatea (0,06 dB/cm en sílice a 1550 nm), Toronto (cruces en sílice a 1550 nm con como máximo 0,01 dB cada uno) y JOANNEUM RESEARCH (borosilicato, MZI y calentadores, vía de consulta publicada).
3. Barreras: MSU (la UE suspendió en 2022 la cooperación en investigación con entidades rusas), Ephos (su web actual solo dice «Glass Advanced Packaging»), Optoscribe (web inaccesible desde esta red) y varios grupos chinos sin página de contacto verificada.
4. Aviso antes de enviar nada: la rama `main` del repositorio público no tiene archivo LICENSE (la API de GitHub devuelve license = null); el Apache-2.0 solo está en la rama `agent/scientific-closure-20261012`, 3 commits por delante. Hay que fusionarla o enlazar esa rama.
5. No se ha contactado a nadie ni se ha enviado ningún formulario. Al final hay dos borradores de correo (inglés y español, menos de 220 palabras) para que los envíes tú, con tu autorización expresa en cada caso.

## Scope and method

- Retrieved 2026-10-13. Public information only: Crossref, OpenAlex, arXiv, GitHub API, official institutional and company pages, and trade press where marked. Nobody was contacted and no form or message was submitted. Only institutional or company page URLs are listed; no personal email addresses or phone numbers were collected.
- Needs from the partner (from `Docs/CIERRE-20261012/T28-FABRICATION-DOSSIER.md`): fs writing in fused silica or borosilicate, trench (type III) guides, couplers, crossings, 3D routing, ideally thermal shifters; characterization at 1550 nm (cut-back, near-field, index profile, crossings, 4x4 transfer matrix); openness to collaboration or external users.
- Every DOI below was re-fetched from `https://api.crossref.org/works/<doi>` on the retrieval date (34 DOIs, 0 failures). Where an abstract was not available the table says the paper was not read.
- Fit score rubric (1-5), applied to this specific ask (a small pilot with cut-back at 1550 nm, co-authorship, open data):
  - **5**: Documents fs-writing in silica or borosilicate near 1550 nm AND trench/depressed-cladding or equivalent AND a stated route for external users AND cut-back/near-field metrology AND no major barrier. No candidate reached 5.
  - **4**: Strong documented capability for most of the ask plus either a stated external-user/contract route or an obvious academic fit; at most one important gap.
  - **3**: Relevant capability but a material gap: other glass or wavelength, no stated external route, or unclear whether the group fabricates in-house.
  - **2**: Weak or indirect evidence, the official page does not state the capability, or a significant practical barrier.
  - **1**: Not suitable now.

## Points the owner should know before any contact

1. **Licence.** The public repository's default branch has no LICENSE file: the GitHub API returns license = null and /contents/LICENSE on main gives 404. An Apache-2.0 LICENSE exists on the branch agent/scientific-closure-20261012, which is 3 commits ahead of main (compare API, 2026-10-13). Docs/CIERRE-20261012/T28-FABRICATION-DOSSIER.md exists on both branches. Merge the licence commit to main (or point partners to the branch) before sending any email; otherwise 'open code' cannot be reused legally by the partner.
2. **No candidate scores 5.** The closest are the entries ranked 1 to 8; each lacks at least one of: trench guides in silica or borosilicate, a stated external route, 1550 nm cut-back practice.
3. **Benchmark groups are also competitors.** Milan (programmable meshes), EPFL (0.06 dB/cm) and Toronto (crossings) hold the reference values that H1-SOTA and H-B are measured against; the email makes no novelty claim, consistent with the project's own withdrawn novelty claims.
4. **Commercial services do not give co-authorship by default.** For entries marked commercial, ask for a quote and for permission to publish the raw data under the stated protocol; the email draft is written for academic labs and should be shortened for vendors.
5. **Spanish door first.** ALF-USAL and IO-CSIC are the Spanish groups with verified fs-written guides in glass; the Shandong group (telecom-band depressed cladding in SK1310) is a co-author of ALF-USAL, so a Salamanca contact may open both.

## Ranked table

| # | ID | Candidate | Cat | Country | Fit | Mode | Key evidence | Main barrier |
|---|---|---|---|---|---|---|---|---|
| 1 | B1 | ALF-USAL (Univ. de Salamanca) | B | Spain | 4 | academic collaboration; R&D contract | [10.1364/ome.402271](https://doi.org/10.1364/ome.402271), [10.3390/mi11010010](https://doi.org/10.3390/mi11010010) | Collaborates 'only with those with joined publications or patents'; outside parties are served under paid research contracts; no 1550 nm silica data. |
| 2 | A3 | Politecnico di Milano / CNR-IFN fs-photonics group | A | Italy | 4 | academic collaboration | [10.1515/nanoph-2023-0636](https://doi.org/10.1515/nanoph-2023-0636), [10.1109/JLT.2019.2923126](https://doi.org/10.1109/JLT.2019.2923126) | Competitor on claim (b); no external-user policy found; effort partly in the spin-off Ephos. |
| 3 | A1 | Galatea Lab, EPFL | A | Switzerland | 4 | academic collaboration | [10.1364/OL.557978](https://doi.org/10.1364/OL.557978), [10.1109/cleo/europe-eqec65582.2025.11109929](https://doi.org/10.1109/cleo/europe-eqec65582.2025.11109929) | No stated external-user route; UV recipe, no trench guides documented. |
| 4 | A2 | Herman Group, Univ. of Toronto | A | Canada | 4 | academic collaboration | [10.1109/JLT.2026.3720907](https://doi.org/10.1109/JLT.2026.3720907), [10.1088/2631-7990/ab4d51](https://doi.org/10.1088/2631-7990/ab4d51) | No stated external-user route; crossing data only at 80 degrees. |
| 5 | C4 | JOANNEUM RESEARCH MATERIALS, Weiz | C | Austria | 4 | commercial service / contract research | [10.3390/photonics13080731](https://doi.org/10.3390/photonics13080731) | Contract research (fees not stated); test wavelength and fused silica not documented. |
| 6 | C3 | ANFF OptoFab node (Macquarie) | C | Australia | 4 | user facility | [10.37188/lam.2024.009](https://doi.org/10.37188/lam.2024.009) | Fees and international-user terms unknown (policy PDF unreadable); distance. |
| 7 | C1 | FEMTOprint | C | Switzerland | 4 | commercial service | [femtoprint.ch](https://www.femtoprint.ch/applications/photonics/glass-waveguides.html) | Prices and terms not stated; trench guides and an external blind protocol not mentioned. |
| 8 | C2 | Modular Photonics | C | Australia | 4 | commercial service | [modularphotonics.com](https://modularphotonics.com/) | No academic programme described; its own glass (Aldente) differs from the silica design. |
| 9 | B2 | IO-CSIC Laser Processing Group (+ Zaragoza, UCM, ICV) | B | Spain | 3 | academic collaboration | [10.3390/mi14071370](https://doi.org/10.3390/mi14071370), [10.1109/jlt.2021.3082620](https://doi.org/10.1109/jlt.2021.3082620) | Site mentions neither waveguides nor external users; glasses are phosphate/silicate, not fused silica. |
| 10 | A9 | MQ Photonics, Macquarie | A | Australia | 3 | academic collaboration; via the ANFF OptoFab user facility | [10.37188/lam.2024.009](https://doi.org/10.37188/lam.2024.009) | Page not readable (HTTP 403); same people as C2 and C3. |
| 11 | A4 | PHI Group, Heriot-Watt | A | United Kingdom | 3 | academic collaboration | [10.1364/josab.423727](https://doi.org/10.1364/josab.423727), [10.1364/ao.510293](https://doi.org/10.1364/ao.510293) | Silica results are at 2.0-2.4 um, not 1550 nm; no external-user policy. |
| 12 | A6 | ORC, Univ. of Southampton | A | United Kingdom | 3 | academic collaboration; services and consultancy | [10.1038/s41598-021-03116-y](https://doi.org/10.1038/s41598-021-03116-y) | No current fs-waveguide group identified; latest output found is 2021. |
| 13 | B3 | LeapLab, Univ. de La Laguna | B | Spain | 3 | academic collaboration | [10.1364/ol.484270](https://doi.org/10.1364/ol.484270), [10.1515/nanoph-2022-0665](https://doi.org/10.1515/nanoph-2022-0665) | Own glass-writing set-up unconfirmed; no contact page verified. |
| 14 | A7 | Jena IAP / Fraunhofer IOF / Rostock | A | Germany | 3 | academic collaboration | [10.1364/ome.507230](https://doi.org/10.1364/ome.507230), [10.1063/5.0301051](https://doi.org/10.1063/5.0301051) | No 1550 nm data; no group contact page verified. |
| 15 | A8 | Feng Chen group, Shandong Univ. | A | China | 3 | academic collaboration | [10.1016/j.optmat.2025.116651](https://doi.org/10.1016/j.optmat.2025.116651) | Paper unread (no abstract available); no group page; distance. |
| 16 | A5 | Qiu group, Zhejiang Univ. / Zhejiang Lab | A | China | 3 | academic collaboration | [10.1364/OL.470670](https://doi.org/10.1364/OL.470670), [10.1364/OME.419945](https://doi.org/10.1364/OME.419945) | Test wavelength not stated; current affiliation unclear; distance. |
| 17 | A10 | LAMP team: HUST + SJTU | A | China | 3 | academic collaboration | [10.1038/s41467-026-72316-9](https://doi.org/10.1038/s41467-026-72316-9) | No group or contact page verified; distance. |
| 18 | C8 | Lasers4EU | C | European Union | 2 | user facility network | [lasers4.eu](https://lasers4.eu/become-a-user/how-to-access/) | No fs-waveguide facility identified; eligibility of an independent researcher unconfirmed. |
| 19 | B4 | CEIT-BRTA Photonics Team | B | Spain | 2 | academic collaboration; contract research | [10.1016/j.optlastec.2023.110475](https://doi.org/10.1016/j.optlastec.2023.110475) | Evidence is for gratings and Bessel-beam structures, not waveguides or 1550 nm. |
| 20 | A11 | MSU Quantum Optical Technologies Lab | A | Russia | 2 | academic collaboration | [10.1103/PhysRevApplied.22.064079](https://doi.org/10.1103/PhysRevApplied.22.064079), [10.1364/PRJ.504588](https://doi.org/10.1364/PRJ.504588) | EU suspended research cooperation with Russian entities in 2022 (applicability to a private collaboration unchecked); no 1550 nm data. |
| 21 | C6 | Ephos | C | Italy | 2 | commercial service | [thequantuminsider.com](https://thequantuminsider.com/2024/09/24/glass-based-photonic-chip-startup-ephos-secures-8-5m-to-innovate-quantum-computing-and-ai-infrastructure/), [ephos.io](https://ephos.io/) | Website now says only 'Glass Advanced Packaging'; no service offered. |
| 22 | C7 | LightFab | C | Germany | 2 | commercial service | [lightfab.de](https://lightfab.de/germany/) | Core offer is etched glass; no waveguide service advertised. |
| 23 | C5 | Optoscribe | C | United Kingdom | 2 | commercial service | [laserfocusworld.com](https://www.laserfocusworld.com/articles/2019/03/optoscribe-expands-3d-component-manufacturing-capability-doubles-headcount.html) | Official site unreachable; no recent news; volume transceiver business. |

## Candidate details

### 1. Grupo de Investigación en Aplicaciones del Láser y Fotónica (ALF-USAL) [B1, fit 4/5]

- **Category / country:** B / Spain
- **Institution:** Universidad de Salamanca (recognised research group; consolidated research unit UIC016)
- **Leads as publicly listed:** Carolina Romero and Javier Rodríguez Vázquez de Aldana (authors of the cited papers); Luis Plaja Rustein (group leader per the Junta de Castilla y León science portal; the group's own site does not name a leader, so check)
- **Why it fits:** Most Spanish fs-writing output in the OpenAlex search of 2026-10-13 (44 works since 2019 for 'femtosecond laser written waveguide' with a USAL author). Official site lists the research line 'Device manufacturing for integrated photonics', two Ti:sapphire CPA systems (800 nm; 1 kHz/120 fs and, since 2019, 5 kHz/60 fs) and a 3-axis workstation 'for manufacturing photonic devices and precision microprocessing' (its laser parameters are not stated). Verified glass work: 2D and 3D Y-splitters and single-mode guides in Er/Yb oxyfluoride nano-glass ceramics (1.6 dB/cm, visible/NIR). Depressed-cladding writing is documented, in crystals (tapered circular cladding in Nd:YAG).
- **Evidence:**
  - [10.1364/ome.402271](https://doi.org/10.1364/ome.402271) - Vázquez de Aldana, Romero et al., "Femtosecond laser direct inscription of 3D photonic devices in Er/Yb-doped oxyfluoride nano-glass ceramics", Optical Materials Express 10(10), 2695 (2020). Crossref OK. Fs inscription of 2D/3D Y-splitters in Er/Yb nano-glass ceramics; 1.6 dB/cm; abstract read.
  - [10.3390/mi11010010](https://doi.org/10.3390/mi11010010) - Romero, García Ajates, Vázquez de Aldana, "Fabrication of Tapered Circular Depressed-Cladding Waveguides in Nd:YAG Crystal by Femtosecond-Laser Direct Inscription", Micromachines 11(1), 10 (2019). Crossref OK. Tapered circular depressed-cladding waveguides in Nd:YAG (crystal); title and authors only.
  - [10.1016/j.rinp.2021.104897](https://doi.org/10.1016/j.rinp.2021.104897) - Sun, ..., Romero, Vázquez de Aldana, Chen, "Tapered depressed-cladding waveguide lasers modulated by Ag nanoparticles embedded in SiO2", Results in Physics 30, 104897 (2021). Crossref OK. Tapered depressed-cladding waveguide lasers with Ag nanoparticles embedded in SiO2; collaboration with the Shandong group; abstract not read, host material of the guides not verified.
  - [10.1063/5.0221394](https://doi.org/10.1063/5.0221394) - Bonduelle, ..., Vázquez de Aldana, Arroyo Heras, Romero, "A route to an all direct laser written integrated FTS (SWIFTS) in the 3.39–4.1 μm range", APL Photonics 9(10), 101302 (2024). Crossref OK. All-DLW building blocks at 3.39-4.1 um (ALF-USAL affiliation confirmed in Crossref); not 1550 nm.
- **Public pages:** group page https://laser.usal.es/alf/en/home/; contact page https://laser.usal.es/alf/en/contact/; other: https://laser.usal.es/alf/en/who-we-are/experimental-equipment/, https://laser.usal.es/alf/en/research/collaborations/, https://laser.usal.es/alf/en/rdcontracts/
- **Collaboration mode:** academic collaboration; R&D contract (services under a research contract, per its collaborations page)
- **Known barrier:** Its collaborations page says it collaborates with other groups 'only with those with joined publications or patents' and serves companies and institutions under research contracts, so a first contact from an independent researcher may be routed to a paid contract. No low-loss silica or borosilicate recipe at 1550 nm and no cut-back set-up are documented on the site (listed instruments: spectrometers, M2, beam profiler, LIBS). Sources are 1-5 kHz class, not the high-repetition-rate regime of the best published silica results.
- **Fit 4/5:** Spanish, documented depressed-cladding experience and a stated contract route; silica/borosilicate loss at 1550 nm is not yet shown by them.
- **Not verified:** current group leader; whether workstation 2 can write fused silica or borosilicate at 1550 nm quality; any fee

### 2. Femtosecond laser micromachining and integrated photonics group, Politecnico di Milano (Physics) and CNR-IFN Milan [A3, fit 4/5]

- **Category / country:** A / Italy
- **Institution:** Politecnico di Milano (Dipartimento di Fisica) and Istituto di Fotonica e Nanotecnologie, CNR (IFN-CNR), Milan
- **Leads as publicly listed:** Roberto Osellame (IFN-CNR Director of Research; Politecnico di Milano profile); Andrea Crespi (Politecnico di Milano); Francesco Ceccarelli, Giacomo Corrielli (IFN-CNR); Ciro Pentangelo (authors of the cited papers)
- **Why it fits:** Universal photonic processors written by fs laser and calibrated at 785 nm and 1550 nm; thermal phase shifters with isolation trenches; borosilicate PICs. Closest match to coupons C and F and also the benchmark for claim (b). Founders of the company Ephos (entry C6) come from this group (press, 2024).
- **Evidence:**
  - [10.1515/nanoph-2023-0636](https://doi.org/10.1515/nanoph-2023-0636) - Pentangelo, ..., Crespi, Osellame, "High‐fidelity and polarization‐insensitive universal photonic processors fabricated by femtosecond laser writing", Nanophotonics 13(12), 2259-2270 (2024). Crossref OK. Universal photonic processors at 785 nm and 1550 nm, average amplitude fidelity 0.9970 at 1550 nm; abstract read.
  - [10.1109/JLT.2019.2923126](https://doi.org/10.1109/JLT.2019.2923126) - Ceccarelli, ..., Osellame, "Thermal Phase Shifters for Femtosecond Laser Written Photonic Integrated Circuits", Journal of Lightwave Technology 37(17), 4275-4281 (2019). Crossref OK. Thermal phase shifters for fs-written circuits.
  - [10.1002/lpor.202000024](https://doi.org/10.1002/lpor.202000024) - Ceccarelli, ..., Crespi, Osellame, "Low Power Reconfigurability and Reduced Crosstalk in Integrated Photonic Circuits Fabricated by Femtosecond Laser Micromachining", Laser & Photonics Reviews 14(10), 2000024 (2020). Crossref OK. Low-power reconfigurability and reduced crosstalk with trenches (power values per T26, not re-read here).
  - [10.1088/2515-7647/ad82c2](https://doi.org/10.1088/2515-7647/ad82c2) - Ceccarelli, ..., Corrielli, "Integrated thermo-optic phase shifters for laser-written photonic circuits operating at cryogenic temperatures", Journal of Physics: Photonics 6(4), 045023 (2024). Crossref OK. Programmable glass PIC with thermo-optic phase shifters at room and cryogenic temperature; abstract read.
  - [10.1117/1.AP.8.1.016009](https://doi.org/10.1117/1.AP.8.1.016009) - Peri, ..., Corrielli, Vallone, "High-performance heterodyne receiver for quantum information processing in a laser-written integrated photonic platform", Advanced Photonics 8(01), 1-17 (2026). Crossref OK. Fs micromachining on borosilicate glass as a PIC platform (Politecnico/CNR-IFN co-authors); abstract read.
- **Public pages:** group page https://www.fisi.polimi.it/en/staff/roberto.osellame; contact page https://www.ifn.cnr.it/where-we-are/milano/; other: https://www.ifn.cnr.it/
- **Collaboration mode:** academic collaboration (route not stated on the pages read)
- **Known barrier:** Direct competitor on claim (b) (programmable fs-written meshes), so the conversation would be about complementarity. No external-user policy found. Part of the group's effort now goes to the spin-off Ephos, whose current website states only 'Glass Advanced Packaging'.
- **Fit 4/5:** Only group with published thermal-shifter meshes at 1550 nm in this glass family; access route unknown.
- **Not verified:** external-user policy; whether trench (depressed-cladding) guides in silica are in their current portfolio

### 3. Galatea Laboratory, EPFL [A1, fit 4/5]

- **Category / country:** A / Switzerland
- **Institution:** École polytechnique fédérale de Lausanne (EPFL), Neuchâtel (per the IEEE metadata of the CLEO/Europe 2025 record)
- **Leads as publicly listed:** Yves Bellouard (leads the Galatea lab; Richemont chair); Lisa Ackermann (first author)
- **Why it fits:** Best verified propagation loss at 1550 nm in fused silica: 0.06 +/- 0.02 dB/cm by cut-back (13 cm to 2.5 cm, SMF-28 butt coupling), written with 450 fs UV (343 nm) pulses at two orders of magnitude higher speed than IR practice. Value read in the open full text by the T26 second reader; the Crossref abstract says 'below 0.1 dB/cm'.
- **Evidence:**
  - [10.1364/OL.557978](https://doi.org/10.1364/OL.557978) - Ackermann, Hermann, Echarri, Gribaudo, Bellouard, "High-speed femtosecond UV laser writing of low-loss waveguides in fused silica", Optics Letters 50(8), 2506 (2025). Crossref OK. UV fs writing of low-loss waveguides in fused silica; affiliation not in Crossref, Galatea confirmed through the same first author's CLEO record below.
  - [10.1109/cleo/europe-eqec65582.2025.11109929](https://doi.org/10.1109/cleo/europe-eqec65582.2025.11109929) - Ackermann, Bellouard, "On the Use of UV Femtosecond Pulses to Write Waveguides in Fused Silica", 2025 Conference on Lasers and Electro-Optics Europe & European Quantum Electronics Conference (CLEO/Europe-EQEC), 1-1 (2025). Crossref OK. Crossref affiliation: EPFL, Galatea Laboratory, Neuchâtel.
- **Public pages:** group page https://www.epfl.ch/labs/galatea/; contact page https://www.epfl.ch/labs/galatea/contact-us/; other: https://people.epfl.ch/Yves.Bellouard
- **Collaboration mode:** academic collaboration
- **Known barrier:** Lab page makes no statement on external users or industry access. Their record is for single guides written with a UV recipe; depressed-cladding guides are not documented.
- **Fit 4/5:** Reference-quality silica loss and cut-back practice at 1550 nm; a trench-guide pilot would be a new request to them.
- **Not verified:** trench guides; willingness to host an external pilot

### 4. Herman Group, University of Toronto [A2, fit 4/5]

- **Category / country:** A / Canada
- **Institution:** University of Toronto, Department of Electrical and Computer Engineering
- **Leads as publicly listed:** Peter R. Herman (leads the group); Gligor Djogo, Amir Rahimnouri (authors)
- **Why it fits:** Fused silica at 1550 nm: waveguide crossings with at most 0.01 dB per intersection up to 16 crossings at 80 degrees, crosstalk below the 40 dB noise floor (arXiv:2512.01972v1, read by T26); 0.2 dB/cm insertion loss minus coupling in the interposer waveguides. Directly relevant to coupon B.
- **Evidence:**
  - [10.1109/JLT.2026.3720907](https://doi.org/10.1109/JLT.2026.3720907) - Djogo, Rahimnouri, Herman, "Laser Structured Optical Interposer for Ultra-Dense Surface Coupling of Multicore Fibers to Silicon Photonic Chip", Journal of Lightwave Technology 44(18), 7978-7986 (2026). Crossref OK. Silica interposer for multicore fibre to silicon photonics; affiliation University of Toronto (Crossref).
  - [10.1088/2631-7990/ab4d51](https://doi.org/10.1088/2631-7990/ab4d51) - Djogo, Li, Ho, ..., Herman, "Femtosecond laser additive and subtractive micro-processing: enabling a high-channel-density silica interposer for multicore fibre to silicon-photonic packaging", International Journal of Extreme Manufacturing 1(4), 045002 (2019). Crossref OK. 84-channel fused-silica interposer by fs additive and subtractive processing; 0.3 dB/cm per T26.
- **Public pages:** group page https://photonics.light.utoronto.ca/laserphotonics; contact page https://photonics.light.utoronto.ca/laserphotonics/contact.html
- **Collaboration mode:** academic collaboration
- **Known barrier:** Group page states no external-user or industry policy and does not describe equipment. Crossing data are at 80 degrees only; shallow angles and 3D overpasses are not documented.
- **Fit 4/5:** Closest published data for crossing loss in fused silica at 1550 nm; a crossings coupon fits their work better than trench guides.
- **Not verified:** trench guides; external-user policy

### 5. JOANNEUM RESEARCH, MATERIALS: Light and Optical Technologies (Weiz) [C4, fit 4/5]

- **Category / country:** C / Austria
- **Institution:** JOANNEUM RESEARCH Forschungsgesellschaft mbH, Institute MATERIALS, Weiz
- **Leads as publicly listed:** Wolfgang Nemitz (head of Light and Optical Technologies per the institute page); Philip Lichtenegger, Bernhard Lamprecht (authors)
- **Why it fits:** Borosilicate glass, single-scan waveguides, directional couplers and Mach-Zehnder interferometers at 30 mm/s; fs-laser-induced etching makes suspended microbridges with microheaters giving a full 2 pi shift at about 17 mW. That matches coupons C and F (thermal shifters with isolation). The institute publishes a feasibility-check route for external partners and calls its Light and Integration Laboratory 'open to industrial partners'.
- **Evidence:**
  - [10.3390/photonics13080731](https://doi.org/10.3390/photonics13080731) - Lichtenegger, Hurdax, Spernbauer, Lamprecht, "Reconfigurable Photonic Integrated Circuits in Glass by Femtosecond Laser Writing and Laser-Induced Chemical Etching", Photonics 13(8), 731 (2026). Crossref OK. Reconfigurable PICs in borosilicate by FLW + FLICE; abstract read (open access). Test wavelength and propagation loss are not in the abstract.
- **Public pages:** group page https://www.joanneum.at/en/materials/; contact page https://www.joanneum.at/en/kontakt/; other: https://www.joanneum.at/materials/en/technical-project-and-feasibility-check/
- **Collaboration mode:** commercial service / contract research (feasibility check first)
- **Known barrier:** Contract research organisation: fees and lead time are not stated; academic co-authorship terms would have to be negotiated. 1550 nm operation and fused silica are not documented in the abstract.
- **Fit 4/5:** EU partner with borosilicate guides, couplers, MZIs and integrated heaters plus a published request route; wavelength still to be confirmed.
- **Not verified:** operating wavelength; propagation loss; price; fused silica capability

### 6. ANFF OptoFab node (Macquarie University headquarters) [C3, fit 4/5]

- **Category / country:** C / Australia
- **Institution:** Australian National Fabrication Facility, OptoFab node (Macquarie University, with Adelaide, ANU and Sydney centres as listed)
- **Leads as publicly listed:** Simon Gross (named as node director on the ANFF node page; other pages name Michael Withford as director); Benjamin Johnston (facility manager)
- **Why it fits:** The only user facility found with 'laser inscription of photonic devices' as a listed speciality and a published access route (short project proposal to the facility manager, assisted or unassisted use). ANFF equipment page lists a custom femtosecond micromachining facility and a tuneable (I-OPA) ultrafast laser inscription facility at the Macquarie node (specifications not on the page read).
- **Evidence:**
  - [10.37188/lam.2024.009](https://doi.org/10.37188/lam.2024.009) - Ross-Adams, Fernandez, Withford, Gross, "Low bend loss, high index, composite morphology ultra-fast laser written waveguides for photonic integrated circuits", Light: Advanced Manufacturing 5(1), 52 (2024). Crossref OK. Macquarie authors; boro-aluminosilicate guides with the 1 dB/cm bend-loss radius reduced from 10 mm to 4 mm at 1550 nm (arXiv:2401.03382 abstract read).
- **Public pages:** group page https://anff.org.au/locations/optofab-node; contact page https://anff.org.au/get-in-touch/; other: https://anff.org.au/access-to-facilities/, https://anff.org.au/equipment/laser-engraving-and-cutting
- **Collaboration mode:** user facility
- **Known barrier:** The access-and-pricing policy PDF could not be read (image-only), so fees and international-user terms are unknown. Time zone and sample shipping. Fabrication would be by node staff or the owner's own visit; 1550 nm metrology is not listed on the pages read.
- **Fit 4/5:** Explicit external-user route and fs-inscription speciality; cost, metrology and international terms to confirm.
- **Not verified:** fees; international user terms; laser specifications; who would run the cut-back

### 7. FEMTOprint (glass waveguides, prototyping and contract manufacturing) [C1, fit 4/5]

- **Category / country:** C / Switzerland (per the .ch company site)
- **Institution:** FEMTOprint SA
- **Leads as publicly listed:** not stated on the pages read
- **Why it fits:** Own page 'Glass waveguides': materials fused silica, Borofloat 33 and Eagle XG; wavelength range 650-1550 nm; propagation losses '<0.2dB/cm'; minimum bend radius 20-25 mm at 1000-1550 nm; directional couplers, MMIs, spot-size converters, fan-in/fan-out, multi-layer routing within one wafer. Services listed: contract development, contract manufacturing, rapid prototyping.
- **Evidence:**
  - https://www.femtoprint.ch/applications/photonics/glass-waveguides.html - FEMTOprint website, read 2026-10-13. Specifications quoted above, as stated by the company; waveguide crossings and depressed-cladding are not stated.
- **Public pages:** group page https://www.femtoprint.ch/applications/photonics.asp; contact page https://www.femtoprint.ch/contacts.php; other: https://www.femtoprint.ch/applications/photonics/glass-waveguides.html
- **Collaboration mode:** commercial service
- **Known barrier:** Pricing, minimum order, lead times and waveguide-specific prototyping terms are not stated. Trench (type III) guides and a customer-run blind cut-back are not mentioned; co-authorship is not part of a normal commercial order.
- **Fit 4/5:** Official page matches material, wavelength and component list; cost and willingness to follow an external preregistered protocol unknown.
- **Not verified:** price; lead time; crossings; trench guides

### 8. Modular Photonics (Macquarie University spin-out) [C2, fit 4/5]

- **Category / country:** C / Australia
- **Institution:** Modular Photonics Pty Ltd, Sydney
- **Leads as publicly listed:** Michael Withford (CEO); Simon Gross (CTO); Nicolas Riesen (co-founder)
- **Why it fits:** Offers custom design, fabrication, testing and packaging of 3D photonic circuits (turnaround 'a few weeks' on its product page); says it 'caters to the photonics research community'; licensed SCHOTT 'Aldente Glass', described as purpose-engineered for ultra-low-loss photonic chips and ultrafast laser inscription. A mode multiplexer product is listed at 1550 nm.
- **Evidence:**
  - https://modularphotonics.com/ - Modular Photonics website, read 2026-10-13. Products OMPlex, LPMUX (1550 nm), MCMUX, custom PICs; Aldente glass licence.
- **Public pages:** group page https://modularphotonics.com/; contact page https://www.modularphotonics.com/contact-us/; other: https://www.modularphotonics.com/about-us/
- **Collaboration mode:** commercial service
- **Known barrier:** No academic pricing or formal research-collaboration programme described. Its own glass (SCHOTT Aldente) is a different material from the dossier's n = 1.444 silica design, and whether fused silica is accepted is not stated.
- **Fit 4/5:** Fast custom fs-written chips from a team that publishes low-bend-loss work; material and cost differ from the dossier.
- **Not verified:** price; fused silica availability; 1550 nm propagation-loss data

### 9. Laser Processing Group (LPG), Instituto de Óptica 'Daza de Valdés', CSIC (with collaborators at Universidad de Zaragoza, Universidad Complutense de Madrid and ICV-CSIC) [B2, fit 3/5]

- **Category / country:** B / Spain
- **Institution:** Instituto de Óptica (IO-CSIC), Madrid
- **Leads as publicly listed:** Javier Solís, Jan Siegel, Rosalía Serna (Research Professors on the group's people page); Antonio Dias-Ponte (IO-CSIC); Juan A. Vallés, David Benedicto (Universidad de Zaragoza, I3A); Belén Sotillo, Jesús del Hoyo (Universidad Complutense de Madrid); Francisco Muñoz (ICV-CSIC), as authors
- **Why it fits:** fs-written guides in glass with a 1534 nm device: twin-core directional coupler in Er/Yb phosphate glass, coupling ratio tuned 100/0 to 50/50 by pumping; multicore active guides; tapers by element redistribution; thermophoretic writing in compositionally designed silicate glass with index contrast up to 2.5e-2. The group's facilities page lists an Ultrafast Materials Processing Laboratory with a Ti:sapphire amplifier (about 100 fs, 800 nm, 1 kHz).
- **Evidence:**
  - [10.3390/mi14071370](https://doi.org/10.3390/mi14071370) - Benedicto, Martín, Dias-Ponte, Solís, Vallés, "An Integrated Pump-Controlled Variable Coupler Fabricated by Ultrafast Laser Writing", Micromachines 14(7), 1370 (2023). Crossref OK. Integrated pump-controlled coupler at 1534 nm in Er3+/Yb3+ phosphate glass; Crossref affiliations: Universidad de Zaragoza (I3A) and IO-CSIC Laser Processing Group.
  - [10.1109/jlt.2021.3082620](https://doi.org/10.1109/jlt.2021.3082620) - Benedicto, Dias, Martín, Vallés, Solís, "Characterization of Multicore Integrated Active Waveguides Written in an Er3+/Yb3+ Codoped Phosphate Glass", Journal of Lightwave Technology 39(15), 5061-5068 (2021). Crossref OK. Multicore integrated active waveguides in Er/Yb phosphate glass; authors and title only.
  - [10.1109/jlt.2020.3015013](https://doi.org/10.1109/jlt.2020.3015013) - Macias-Montero, Dias, Sotillo, ..., Solís, "Waveguide Tapers Fabrication by Femtosecond Laser Induced Element Redistribution in Glass", Journal of Lightwave Technology 38(23), 6578-6583 (2020). Crossref OK. Waveguide tapers by fs-induced element redistribution in glass; authors and title only.
  - [10.1038/s41598-021-87765-z](https://doi.org/10.1038/s41598-021-87765-z) - Macias-Montero, Muñoz, Sotillo, del Hoyo, ..., Siegel, Solís, "Femtosecond laser induced thermophoretic writing of waveguides in silicate glass", Scientific Reports 11(1), 8390 (2021). Crossref OK. Thermophoretic writing of IR waveguides in designed silicate glass; abstract read.
- **Public pages:** group page https://lpg.io.csic.es/; contact page https://www.io.csic.es/research/project-and-knowledge-management-office-contact-point/; other: https://lpg.io.csic.es/people/, https://lpg.io.csic.es/facilities/
- **Collaboration mode:** academic collaboration
- **Known barrier:** The group site does not mention waveguide writing or external users; its facilities list an 800 nm, 1 kHz amplifier. Their recent guides are in phosphate and designed silicate glasses, not fused silica or Eagle XG. Current affiliation of Macías-Montero not verified.
- **Fit 3/5:** Spanish and active in fs-written passive and active guides in glass at 1534 nm, but not in fused silica and no stated external route.
- **Not verified:** fused silica or Eagle XG capability; cut-back set-up at 1550 nm; access terms

### 10. MQ Photonics, Macquarie University (Withford, Gross) [A9, fit 3/5]

- **Category / country:** A / Australia
- **Institution:** Macquarie University, School of Mathematical and Physical Sciences, Sydney
- **Leads as publicly listed:** Michael J. Withford; Simon Gross; Andrew Ross-Adams, Toney T. Fernandez (authors)
- **Why it fits:** Composite-morphology fs-written guides in boro-aluminosilicate glass: positive index change 1.12e-2 and the 1.0 dB/cm bend-loss radius reduced from 10 mm to 4 mm at 1550 nm (arXiv:2401.03382, abstract read). The same people run the OptoFab node (C3) and Modular Photonics (C2), so a request goes through one door.
- **Evidence:**
  - [10.37188/lam.2024.009](https://doi.org/10.37188/lam.2024.009) - Ross-Adams, Fernandez, Withford, Gross, "Low bend loss, high index, composite morphology ultra-fast laser written waveguides for photonic integrated circuits", Light: Advanced Manufacturing 5(1), 52 (2024). Crossref OK. Affiliation MQ Photonics, Macquarie University (OpenAlex); abstract from arXiv:2401.03382.
- **Public pages:** group page https://www.mq.edu.au/faculty-of-science-and-engineering/departments-and-schools/school-of-mathematical-and-physical-sciences/our-research/mq-photonics/skills-and-capabilities; contact page https://anff.org.au/get-in-touch/
- **Collaboration mode:** academic collaboration; via the ANFF OptoFab user facility
- **Known barrier:** The Macquarie page returned HTTP 403 to the fetch tool, so its text was not read (URL taken from a search listing). Overlaps with C2 and C3.
- **Fit 3/5:** Good 1550 nm glass-guide results; the practical door is the OptoFab node (C3), so scored below it.
- **Not verified:** page content; silica trench guides

### 11. PHotonic Instrumentation (PHI) Group, Institute of Photonics and Quantum Sciences, Heriot-Watt University [A4, fit 3/5]

- **Category / country:** A / United Kingdom
- **Institution:** Heriot-Watt University, Edinburgh
- **Leads as publicly listed:** Robert R. Thomson (head of the group per the PHI site)
- **Why it fits:** Long-running ultrafast laser inscription (ULI) group for astrophotonics, clinical and quantum instruments: 3 dB asymmetric directional couplers in commercial Infrasil silica written with a 1030 nm laser (K-band, 2.0-2.4 um; straight-guide insertion loss about 1.2 +/- 0.5 dB) and fibre-connectorized beam combiners (about 1.1 dB insertion loss over 2-2.3 um).
- **Evidence:**
  - [10.1364/josab.423727](https://doi.org/10.1364/josab.423727) - Benoît, ..., Thomson, "Ultrafast laser inscription of asymmetric integrated waveguide 3 dB couplers for astronomical K-band interferometry at the CHARA array", Journal of the Optical Society of America B 38(9), 2455 (2021). Crossref OK. Couplers in Infrasil silica, 1030 nm writing laser; Thomson affiliation Heriot-Watt (OpenAlex); abstract read.
  - [10.1364/ao.510293](https://doi.org/10.1364/ao.510293) - Siliprandi, MacLachlan, ..., "Fiber-connectorized ultrafast-laser-inscribed K-band integrated optics beam combiner for the CHARA telescope array", Applied Optics 63(1), 159 (2023). Crossref OK. Fibre-connectorized K-band ULI beam combiner; abstract read.
  - [10.1002/lpor.202300702](https://doi.org/10.1002/lpor.202300702) - Sun, Moser, Jesacher, Salter, Thomson, Booth, "Fast, Precise, High Contrast Laser Writing for Photonic Chips with Phase Aberrations", Laser & Photonics Reviews 18(9), 2300702 (2024). Crossref OK. Fast, high-contrast writing scheme in optical glass (Thomson at Heriot-Watt); abstract read.
- **Public pages:** group page https://phi.eps.hw.ac.uk/; contact page https://phi.eps.hw.ac.uk/contacts.html; other: https://phi.eps.hw.ac.uk/members.html
- **Collaboration mode:** academic collaboration
- **Known barrier:** Their silica results are at 2.0-2.4 um, not 1550 nm. The site states no collaboration or external-user policy.
- **Fit 3/5:** Strong silica ULI, coupler and 3D experience; wavelength and application focus differ.
- **Not verified:** 1550 nm results; trench guides; external-user policy

### 12. Optoelectronics Research Centre (ORC), University of Southampton [A6, fit 3/5]

- **Category / country:** A / United Kingdom
- **Institution:** University of Southampton
- **Leads as publicly listed:** Martynas Beresna; Gilberto Brambilla; Timothy Lee, Qi Sun (authors)
- **Why it fits:** Fused-silica fs-written guides at 1550 nm with a microcrack to suppress bend loss: 1 dB/cm at 10 mm radius, stable after one year (abstract read via Europe PMC). T26 lists 0.15 dB/cm propagation loss at 1550 nm from the same paper. ORC states it supports industry with joint projects, consultancy and services, and that its cleanrooms and laser laboratories are available to academia and industry.
- **Evidence:**
  - [10.1038/s41598-021-03116-y](https://doi.org/10.1038/s41598-021-03116-y) - Lee, Sun, Beresna, Brambilla, "Low bend loss femtosecond laser written waveguides exploiting integrated microcrack", Scientific Reports 11(1), 23770 (2021). Crossref OK. Affiliation ORC, University of Southampton (Crossref/OpenAlex).
- **Public pages:** group page https://www.southampton.ac.uk/about/faculties-schools-departments/optoelectronics-research-centre; contact page https://www.southampton.ac.uk/about/contact
- **Collaboration mode:** academic collaboration; services and consultancy (ORC statement)
- **Known barrier:** The ORC page names a laser-direct-write sub-group but no femtosecond waveguide group; the most recent fs-waveguide output found is 2021. Post-Brexit contractual and funding mechanics.
- **Fit 3/5:** Verified 1550 nm silica work and an open-to-industry statement, but no current waveguide group identified.
- **Not verified:** current fs-waveguide group and equipment; output after 2021

### 13. LeapLab (Light-matter interactions and Extreme Application Photonics Laboratory), Universidad de La Laguna [B3, fit 3/5]

- **Category / country:** B / Spain
- **Institution:** Universidad de La Laguna (Departamento de Física; IUDEA), Tenerife
- **Leads as publicly listed:** Airán Ródenas Seguí (leader per the ULL research portal)
- **Why it fits:** Ródenas is a co-author of a 2023 Optics Letters paper on chip-sized silica-glass 3D three-telescope beam combiners in the near-IR (3D routing avoids in-plane crossings) and works on 3D fs nanolithography; a search summary lists a 2025 master's thesis with him as advisor on optimising fs direct writing in fused silica (not opened). Earlier postdoc at Heriot-Watt; collaborates with Osellame's group.
- **Evidence:**
  - [10.1364/ol.484270](https://doi.org/10.1364/ol.484270) - Martin, Zhang, Bonduelle, ..., Rodenas, ..., Stoian, d'Amico, "Development of a 3D ultrafast laser written near-infrared spectro-interferometer", Optics Letters 48(9), 2253 (2023). Crossref OK. Silica-glass 3D beam combiners; Ródenas affiliation Universidad de La Laguna (Crossref); fabrication site is not stated in the abstract.
  - [10.1515/nanoph-2022-0665](https://doi.org/10.1515/nanoph-2022-0665) - Paz-Buclatin, ... (Universidad de La Laguna), "Circularly symmetric nanopores in 3D femtosecond laser nanolithography with burst control and the role of energy dose", Nanophotonics 12(8), 1511-1525 (2023). Crossref OK. 3D fs nanolithography in crystals; ULL affiliations in Crossref.
- **Public pages:** group page https://portalciencia.ull.es/grupos/9234/detalle; contact page not verified; other: https://extremelightblog.com/
- **Collaboration mode:** academic collaboration
- **Known barrier:** The portal page does not list equipment, and the 2023 beam-combiner paper has Grenoble/Lyon co-authors, so it is not verified that LeapLab has its own fs-writing set-up for glass. No contact page verified (portal page and the lab blog only). Focus is crystals and extreme-environment photonics.
- **Fit 3/5:** Spanish, with silica 3D-routing and fs-writing expertise and links to Milan; own in-house glass-writing capacity unconfirmed.
- **Not verified:** in-house fs-writing system for glass; contact page

### 14. Institute of Applied Physics (Friedrich Schiller University Jena) with Fraunhofer IOF Jena, and University of Rostock (Szameit) [A7, fit 3/5]

- **Category / country:** A / Germany
- **Institution:** Friedrich Schiller University Jena; Fraunhofer Institute for Applied Optics and Precision Engineering (IOF); University of Rostock
- **Leads as publicly listed:** Stefan Nolte (Fraunhofer IOF / Jena); Alexander Szameit (Rostock); Alessandro Alberucci, Chandroth P. Jisha (Jena IAP, authors)
- **Why it fits:** Fused-silica fs-written waveguide with an embedded liquid-crystal layer as a tunable waveplate, and single-shot segmented guides in glasses with controllable index contrast. Academic labs that routinely write waveguides in fused silica for photonic devices.
- **Evidence:**
  - [10.1364/ome.507230](https://doi.org/10.1364/ome.507230) - Lammers, Alberucci, Jisha, Szameit, Nolte, "Electro-optical control of polarization in femtosecond-laser written waveguides using an embedded liquid crystal cell", Optical Materials Express 14(4), 836 (2024). Crossref OK. Tunable waveplate in a fused-silica fs-written waveguide; abstract read.
  - [10.1063/5.0301051](https://doi.org/10.1063/5.0301051) - Alasgarzade, Alberucci, Jisha, Nolte, "Single-shot femtosecond-written segmented waveguides in amorphous materials", APL Photonics 10(12), 121301 (2025). Crossref OK. Single-shot segmented waveguides in glasses; abstract read; wavelength not stated.
- **Public pages:** group page https://www.iap.uni-jena.de/; contact page not verified; other: https://www.iof.fraunhofer.de/en.html, https://www.physik.uni-rostock.de/en/
- **Collaboration mode:** academic collaboration
- **Known barrier:** Neither paper reports 1550 nm loss; only institution home pages were verified (HTTP 200), no group contact page. No external-user policy found.
- **Fit 3/5:** Active fs-writing in fused silica with a photonic-device focus; telecom loss data not found.
- **Not verified:** 1550 nm loss data; group contact page; external-user policy

### 15. Femtosecond-laser group of Feng Chen, State Key Laboratory of Crystal Materials, Shandong University [A8, fit 3/5]

- **Category / country:** A / China
- **Institution:** Shandong University, School of Physics, Jinan
- **Leads as publicly listed:** Feng Chen (last author); Jiaxiang Zhou (first author)
- **Why it fits:** The only record found with 'telecom-band depressed-cladding waveguides' in a glass (SK1310) in the title, which is the geometry of the project's trench guides. Co-author with the Salamanca ALF group (for example Results in Physics 2021, entry B1).
- **Evidence:**
  - [10.1016/j.optmat.2025.116651](https://doi.org/10.1016/j.optmat.2025.116651) - Zhou, Liu, Cheng, Du, Wu, Wang, Lu, Zhang, Chen, "Femtosecond laser writing of telecom-band depressed-cladding waveguides and mode modulation in SK1310 glass", Optical Materials 159, 116651 (2025). Crossref OK. Telecom-band depressed-cladding waveguides and mode modulation in SK1310 glass; Shandong University affiliations (OpenAlex); no abstract in Crossref, so loss values were not read.
- **Public pages:** group page http://www.en.phy.sdu.edu.cn/; contact page https://www.phy.sdu.edu.cn/xygk/lxfs.htm
- **Collaboration mode:** academic collaboration
- **Known barrier:** Paper not read (no abstract available); the School of Physics site has no page for the group's waveguide work. Practical: distance, language, shipping; export-control and institutional rules not checked.
- **Fit 3/5:** Directly on-topic geometry at telecom wavelengths, reachable through an existing Salamanca collaboration; details unread.
- **Not verified:** loss values; operating-wavelength numbers; external-user policy

### 16. Jianrong Qiu's femtosecond-laser glass group, Zhejiang University / Zhejiang Lab [A5, fit 3/5]

- **Category / country:** A / China
- **Institution:** Zhejiang University (State Key Laboratory of Modern Optical Instruments) and Zhejiang Lab, Hangzhou
- **Leads as publicly listed:** Jianrong Qiu (ZJU College of Optical Science and Engineering per a 2023 ZJU newsroom item); Dezhi Tan (Zhejiang Lab / ZJU); Xiaoyu Sun, Zengling Li (authors)
- **Why it fits:** Record claim in silica glass: 0.07 dB/cm propagation loss, bend loss 0.001 dB/mm at 30 mm radius, effective writing speed 125 um/s, fan-out devices for 3D integration (abstract read). T26 notes that the 1550 nm attribution comes from citing papers, not from the abstract.
- **Evidence:**
  - [10.1364/OL.470670](https://doi.org/10.1364/OL.470670) - Tan, Sun, Li, Qiu, "Effectively writing low propagation and bend loss waveguides in the silica glass by using a femtosecond laser", Optics Letters 47(18), 4766 (2022). Crossref OK. Affiliations Zhejiang University / Zhejiang Lab (OpenAlex); abstract read.
  - [10.1364/OME.419945](https://doi.org/10.1364/OME.419945) - Tan, Sun, Qiu, "Femtosecond laser writing low-loss waveguides in silica glass: highly symmetrical mode field and mechanism of refractive index change", Optical Materials Express 11(3), 848 (2021). Crossref OK. Low-loss guides in silica glass, symmetric mode field.
- **Public pages:** group page https://www.zju.edu.cn/english/2023/0323/c19573a2731924/page.htm; contact page not verified
- **Collaboration mode:** academic collaboration
- **Known barrier:** Test wavelength not in the abstract; Qiu's current affiliation is inconsistent across sources (ZJU in 2023; co-author Xiaoyu Sun is a PhD student in a Westlake University lab). No contact page verified. Practical: distance, language; export-control and institutional rules not checked.
- **Fit 3/5:** Strong silica results, but unconfirmed wavelength and no verified access route.
- **Not verified:** wavelength of the 0.07 dB/cm value; current affiliation; contact page

### 17. Programmable 3D photonic neural network chip (LAMP): Huazhong University of Science and Technology and Shanghai Jiao Tong University [A10, fit 3/5]

- **Category / country:** A / China
- **Institution:** HUST Wuhan National Laboratory for Optoelectronics / Optics Valley Laboratory; Shanghai Jiao Tong University, Center for Integrated Quantum Information Technologies (IQIT)
- **Leads as publicly listed:** Xian-Min Jin (SJTU); Jianji Dong, Xinliang Zhang (HUST); Ziyu Cao (first author)
- **Why it fits:** 8-layer 8x8 photonic-lantern cascade with heaters in glass, Nature Communications 17, 5476 (2026); T26 records 146 and 161 mW per pi. The SJTU side is an fs-writing group. Closest published match to coupon F in 3D.
- **Evidence:**
  - [10.1038/s41467-026-72316-9](https://doi.org/10.1038/s41467-026-72316-9) - Cao, Du, Yuan, Wu, ..., Jin, Xu, Tang, Dong, Zhang, "Programmable Three-dimensional Photonic Neural Network Chip", Nature Communications 17(1), 5476 (2026). Crossref OK. Affiliations HUST and SJTU (OpenAlex); abstract not in Crossref; heater powers from the T26 records, not re-read.
- **Public pages:** group page https://doi.org/10.1038/s41467-026-72316-9; contact page not verified
- **Collaboration mode:** academic collaboration
- **Known barrier:** No group or contact page verified; paper not read here. Practical: distance, language; export-control and institutional rules not checked.
- **Fit 3/5:** High capability in programmable 3D glass circuits; access path unknown.
- **Not verified:** group page; fabrication glass and wavelength; external-user policy

### 18. Lasers4EU (successor of Laserlab-Europe transnational access) [C8, fit 2/5]

- **Category / country:** C / European Union (office in Germany)
- **Institution:** Lasers4EU consortium; coordination office at the Max Born Institute, Berlin
- **Leads as publicly listed:** not stated on the pages read
- **Why it fits:** Official page: central platform to 27 laser research infrastructures, three routes (single-instrument, multi-instrument, industry), proposals through the ARIA system, travel and accommodation covered per host practice, typical processing four to eight weeks, 20-month validity. A host could offer femtosecond micromachining, but the facility catalogue was not readable.
- **Evidence:**
  - https://lasers4.eu/become-a-user/how-to-access/ - Lasers4EU 'How to access', read 2026-10-13. Access routes and eligibility as quoted; the majority of users must work in a different country from the host.
- **Public pages:** group page https://lasers4.eu; contact page https://lasers4.eu/become-a-user/how-to-access/; other: https://lasers4.eu/become-a-user/call-for-proposals/, https://lasers4.eu/find-a-lab/
- **Collaboration mode:** user facility network (transnational access)
- **Known barrier:** No facility offering fs waveguide writing in glass was identified from the pages read. Access is for visits to a host abroad with scientific-merit review; eligibility of an independent researcher must be confirmed. A Politecnico di Milano project listing seen in search gives the programme dates as Oct 2024 - Sep 2028.
- **Fit 2/5:** Real EU open-access route, but no waveguide-writing facility confirmed.
- **Not verified:** facility catalogue; eligibility of an independent researcher; any fs-waveguide facility

### 19. Photonics Team, CEIT-BRTA (Universidad de Navarra) [B4, fit 2/5]

- **Category / country:** B / Spain
- **Institution:** CEIT-BRTA, San Sebastián, associated with Universidad de Navarra
- **Leads as publicly listed:** Santiago M. Olaizola (leads the Photonics Team in the Microsystems unit since 2003 per a Warwick consortium page; principal investigator on the Universidad de Navarra portal); Jorge Fantova, Ainara Rodríguez (authors)
- **Why it fits:** Fs processing of optical glasses with Bessel beams to generate embedded devices (Optics & Laser Technology 171, 2024); supervised theses on fs-inscribed volume gratings in glass. Applied and industry-facing (works with Basque and Spanish companies per the same Warwick page).
- **Evidence:**
  - [10.1016/j.optlastec.2023.110475](https://doi.org/10.1016/j.optlastec.2023.110475) - Fantova, Rodríguez, del Hoyo, Mandayo, Olaizola, "Bessel beams as a versatile tool to generate embedded devices in optical glasses", Optics & Laser Technology 171, 110475 (2024). Crossref OK. Bessel-beam embedded devices in optical glasses; abstract not in Crossref, content not read.
- **Public pages:** group page https://www.ceit.es/; contact page https://www.ceit.es/acerca-de-ceit/contacto
- **Collaboration mode:** academic collaboration; contract research (technology centre; not verified)
- **Known barrier:** Evidence is for embedded gratings and Bessel-beam structures, not waveguides or 1550 nm; the lab page was not read.
- **Fit 2/5:** Spanish glass fs-processing group, but waveguide and telecom evidence is missing.
- **Not verified:** waveguide writing; 1550 nm; services offered

### 20. Quantum Optical Technologies Laboratory / Quantum Technology Centre, Lomonosov Moscow State University [A11, fit 2/5]

- **Category / country:** A / Russia
- **Institution:** Lomonosov Moscow State University, Moscow
- **Leads as publicly listed:** Sergei P. Kulik (head of the laboratory per its page); Stanislav S. Straupe, Nikolay N. Skryabin, Sergey A. Zhuravitskii (authors)
- **Why it fits:** Fused-silica multiscan guides with 0.07 dB/cm propagation loss at 920 nm (per T26), mode overlap above 98.8 % with SMF, about 0.2 dB per facet, a fibre-coupled 25-channel interferometer under 1 dB insertion loss (arXiv:2408.06688 abstract read); programmable 8-port interferometer with 56 shifters (Photonics Research 2024, with the Russian Quantum Center). Not at 1550 nm.
- **Evidence:**
  - [10.1103/PhysRevApplied.22.064079](https://doi.org/10.1103/PhysRevApplied.22.064079) - Skryabin, Zhuravitskii, Dyakonov, Kalinkin, Straupe, Kulik, "Femtosecond-laser-written low-loss multiscan waveguides in fused silica", Physical Review Applied 22(6), 064079 (2024). Crossref OK. Affiliations absent from Crossref; MSU Quantum Technology Centre per the lab page.
  - [10.1364/PRJ.504588](https://doi.org/10.1364/PRJ.504588) - Kondratyev, ..., Straupe, Kulik, "Large-scale error-tolerant programmable interferometer fabricated by femtosecond laser writing", Photonics Research 12(3), A28 (2024). Crossref OK. 8-port error-tolerant programmable interferometer at 920-980 nm (Russian Quantum Center, South Ural State University); abstract read.
- **Public pages:** group page https://www.qotlabs.org/en/; contact page https://www.qotlabs.org/en/contacts; other: https://ec.europa.eu/commission/presscorner/detail/en/ip_22_1544
- **Collaboration mode:** academic collaboration
- **Known barrier:** On 4 March 2022 the European Commission suspended cooperation with Russian entities in research, science and innovation (no new Horizon Europe contracts or agreements; payments suspended) and, with the fifth sanctions package of 8 April 2022, terminated participation of Russian public bodies in EU programmes. These are EU-programme measures; I did not verify whether they, or any other sanction or export rule, apply to a private collaboration between a Spanish independent researcher and MSU, nor their current status. Practical issues (payments, shipping, travel, institutional approval, reputation) need legal advice.
- **Fit 2/5:** Excellent capability, but a significant legal and practical barrier and no 1550 nm data.
- **Not verified:** current sanctions status for this institution; 1550 nm capability

### 21. Ephos (glass photonic chips, Milan) [C6, fit 2/5]

- **Category / country:** C / Italy (Milan; a US entity is also mentioned in press)
- **Institution:** Ephos (earlier named Faro Quantum Technologies, per press)
- **Leads as publicly listed:** Andrea Rocchetto (founder); Francesco Ceccarelli, Giacomo Corrielli, Roberto Osellame (co-founders), per The Quantum Insider, 24 Sep 2024
- **Why it fits:** Press (24 Sep 2024): a Milan facility for glass-based quantum photonic circuits, 8.5 million USD seed. The founders come from the Politecnico/CNR-IFN group of entry A3.
- **Evidence:**
  - https://thequantuminsider.com/2024/09/24/glass-based-photonic-chip-startup-ephos-secures-8-5m-to-innovate-quantum-computing-and-ai-infrastructure/ - The Quantum Insider, 24 Sep 2024. Company description and founders; the article does not mention femtosecond writing.
  - https://ephos.io/ - Ephos website, read 2026-10-13. Homepage text is only 'Glass Advanced Packaging' with Careers and Contact links; no product or service page, no statement on waveguide chips.
- **Public pages:** group page https://ephos.io/; contact page not verified; other: https://ephos.io/careers
- **Collaboration mode:** commercial service (not stated by the company)
- **Known barrier:** Its current website describes 'Glass Advanced Packaging' and offers no research service; the domain ephos.com is parked for sale. There is no contact page, only a mail link on the homepage (not copied here).
- **Fit 2/5:** Strong team heritage, but nothing the company currently publishes offers external fabrication.
- **Not verified:** any current offer; pricing; access

### 22. LightFab (selective laser-induced etching of glass, Aachen) [C7, fit 2/5]

- **Category / country:** C / Germany
- **Institution:** LightFab GmbH
- **Leads as publicly listed:** not stated on the pages read
- **Why it fits:** Official site: SLE process and 3D glass microfabrication for prototypes, small series and mass production, plus a job-shop; 'waveguide writing' is not stated on the pages read (a third-party profile lists it among the machine's uses).
- **Evidence:**
  - https://lightfab.de/germany/ - LightFab website, read 2026-10-13. SLE technology, prototyping and series, LightFab 3D printer; waveguide writing 'not stated'.
- **Public pages:** group page https://lightfab.de/germany/; contact page https://lightfab.de/germany/
- **Collaboration mode:** commercial service
- **Known barrier:** Core offer is etched glass microstructures, not index-written guides; no waveguide service page or loss data found.
- **Fit 2/5:** Capability on paper (machine) but not advertised by the company.
- **Not verified:** waveguide writing service; loss data

### 23. Optoscribe (laser-written glass photonic components, Livingston) [C5, fit 2/5]

- **Category / country:** C / United Kingdom (Scotland)
- **Institution:** Optoscribe Ltd
- **Leads as publicly listed:** Nick Psaila (CEO in March 2019 trade press)
- **Why it fits:** Trade press 2017-2020: laser direct-write glass-based integrated 3D photonic components for transceivers (multimode fan-outs, multicore-fibre fan-in/fan-out with Sumitomo Electric, OptoCplrLT glass coupling chip); third-generation inscription system in 2019.
- **Evidence:**
  - https://www.laserfocusworld.com/articles/2019/03/optoscribe-expands-3d-component-manufacturing-capability-doubles-headcount.html - Laser Focus World, March 2019 (listed by search; not fetched). Expansion, cleanroom and third-generation inscription system.
- **Public pages:** group page https://www.optoscribe.com/; contact page not verified
- **Collaboration mode:** commercial service (volume component supplier; custom service not verified)
- **Known barrier:** Official site unreachable from this network on 2026-10-13 (connection refused or timeouts), so nothing was read from it; no 2025-2026 news found; business is high-volume transceiver parts.
- **Fit 2/5:** Real fs-writing company, but no evidence of research-scale custom runs.
- **Not verified:** current status; custom prototyping offer; contact page

## Checked and not ranked

| Group or facility | Country | Reason |
|---|---|---|
| Universidad de Zaragoza, I3A (Juan A. Vallés, David Benedicto) | Spain | Co-author with IO-CSIC on the 1534 nm coupler (10.3390/mi14071370); fabrication affiliation is IO-CSIC, so folded into B2. No independent fs-writing equipment found. |
| Universidad Complutense de Madrid, Física de Materiales (Belén Sotillo, Jesús del Hoyo) | Spain | Co-authors of the IO-CSIC thermophoretic-writing papers; folded into B2. No group page or equipment page found. |
| ICV-CSIC (Instituto de Cerámica y Vidrio; Francisco Muñoz) | Spain | Glass-composition partner in the IO-CSIC papers (10.1038/s41598-021-87765-z); a possible supplier of designed glasses, not a writing lab. |
| ICFO (Hugues de Riedmatten, Samuele Grandi) | Spain | User of laser-written circuits made in Milan (10.1088/2515-7647/ad82c2); no in-house fs-writing in glass found. |
| Universidad Politécnica de Madrid, Laser Micro- and Nano-manufacturing Laboratory (manager Carlos Molpeceres) | Spain | Page lists a 1030 nm femtosecond source (EKSPLA Femtolux 30) and 'any type of material'; glass and waveguide writing not stated, no fs-waveguide publication found. Contact route: https://www.upm.es/recursosidi/solicitud |
| Universitat Jaume I; Universitat de València; Universitat Politècnica de València | Spain | OpenAlex hits are fibre Bragg gratings, fibre sensors and users of Heriot-Watt photonic lanterns, not planar fs-written guides in glass. |
| Universitat Rovira i Virgili (FiCMA; Xavier Mateos, Magdalena Aguiló, Francesc Díaz) | Spain | Crystal waveguide lasers, written with the Salamanca group; no glass work found. |
| Universidad de Cantabria (Photonics Engineering Group) | Spain | Ultrafast inscription in optical fibres, not planar glass. |
| Centro de Láseres Pulsados (CLPU), Salamanca (ICTS) | Spain | Competitive open access through its FARO application (VEGA petawatt systems); ALF-USAL lists it as a collaborator and the CDTI catalogue names a ULAMP micro-processing service (not read). No waveguide capability verified. https://www.clpu.es/ |
| Leibniz-Institut für Astrophysik Potsdam (AIP), ultrafast laser inscription facility | Germany | arXiv:2609.16419 (2026) commissions type-I waveguide writing in silica glass for the J-band (1300-1400 nm); propagation loss not reported; external access not stated. |
| Vilnius University Laser Research Center, femtosecond micromachining facility | Lithuania | Four Yb:KGW sources (1030 nm with harmonics); waveguide writing not explicitly stated; the Center lists Laserlab-Europe open-access status. https://www.ff.vu.lt/en/lrc/expertise-and-services/femtosecond-micromachining-facility |
| Translume (Ann Arbor) | United States | Website advertises fused-silica micromachining, microfluidics and ion traps; waveguides and wavelengths not stated. Contact page https://translume.com/contact |
| Shanghai Optoweave Technology (company co-author of 10.1002/adpr.70241) | China | Paper reports 0.13 dB/cm waveguides and 0.06 dB coupling loss at 1310 nm in a 3D glass FI/FO chip; company services not assessed. |
| ACTPHAST 4.0 | European Union | SME-oriented photonics innovation hub; sources conflict on whether it still operates (end dates 2021-2023 listed); no fs-glass service confirmed. |

## What could not be verified

- Optoscribe: official site unreachable from this network (connection refused or timeouts); description is from 2017-2020 trade press only.
- Ephos: current homepage says only 'Glass Advanced Packaging'; the 2024 press description (glass quantum photonic circuits, Milan) could not be matched to any current service. ephos.com is parked for sale; the company site is ephos.io.
- Macquarie MQ Photonics page returned HTTP 403 to the fetch tool; the ANFF OptoFab access-and-pricing PDF is image-only and unreadable; no fee or international-user term was read for ANFF.
- Modular Photonics contact page returns 403 to scripted requests (read with the fetch tool, which succeeded).
- Test wavelength not in the abstract: Joanneum (borosilicate PICs), Tan/Qiu (0.07 dB/cm), Jena/Rostock papers; Zhou et al. (Shandong, telecom-band depressed cladding) has no abstract in Crossref or OpenAlex, so no loss value was read.
- Affiliation of Ackermann et al. (Opt. Lett. 50, 2506) is empty in Crossref and OpenAlex; EPFL Galatea was confirmed through the same first author's CLEO/Europe 2025 record (DOI 10.1109/cleo/europe-eqec65582.2025.11109929).
- ALF-USAL: the group site names no leader; the regional science portal names Luis Plaja Rustein and may be out of date.
- LeapLab (ULL): no equipment page or confirmed in-house fs-writing system for glass; HUST/SJTU, Zhejiang and Jena/Rostock: no group contact page verified.
- OptoFab node director: the ANFF node page names Simon Gross, other sources name Michael Withford.
- No prices, lead times or availability were read for any commercial entity (FEMTOprint, Modular Photonics, Joanneum, LightFab, Optoscribe, Ephos).
- MSU: the EU measures cited are from the Commission's March and April 2022 announcements; current status and applicability to a private collaboration were not checked.
- Details from T26 (records.json) were not re-read: 0.15 dB/cm (Southampton), 0.07 dB/cm at 920 nm (MSU), heater powers (LAMP, Milan), 56 shifters (Kondratyev).
- The JEV advisory step of the global workflow was not run for this literature and web search; the ranking and scores are my own judgement from the evidence above, not a JEV decision.

## Outreach email drafts (for the owner to send himself)

Neither draft has been sent. Replace the bracketed name; send the Spanish one to Spanish groups. Before sending, resolve the licence point above and confirm that the repository link shows the dossier on the branch you choose. Each draft has 207 (English) and 213 (Spanish) words, including subject, greeting and signature.

### English

```text
Subject: Request for a small pilot: fs-written trench waveguides in silica, cut-back at 1550 nm

Dear [Prof./Dr. Name],

I am Francisco Angulo de Lafuente, an independent researcher in Spain. I am looking for a laboratory to run one physical test for an open study of femtosecond-laser-written optical networks in glass.

Already public: a preregistered numerical study; four registered tests designed to refute its own claims (one withdrew an energy-advantage claim); a verified literature review; registered predictions of the 1550 nm loss of trench (depressed-cladding) guides, fixed before any measurement; and a fabrication dossier.

The request: a pilot run of about three chips with straight trench guides at four lengths (1-4 cm), written in the glass and with the laser recipe you judge best, plus a cut-back measurement at 1550 nm. Optionally, a coupon of waveguide crossings in series. I do not prescribe writing parameters.

In return: co-authorship under CRediT roles agreed beforehand, open raw data and code, and a registered prediction that your data can confirm or refute. Negative results are published on the same terms.

Repository and dossier: https://github.com/Agnuxo1/Silice-Neuro3D-Cube (Docs/CIERRE-20261012/T28-FABRICATION-DOSSIER.md)

If this fits your group, or you know who it would fit, I would be grateful for a short reply.

Kind regards,
Francisco Angulo de Lafuente
```

### Español

```text
Asunto: Propuesta de un piloto: guías de trinchera escritas con láser de femtosegundo en sílice, medida cut-back a 1550 nm

Estimado/a [Prof./Dr./Dra. Nombre]:

Soy Francisco Angulo de Lafuente, investigador independiente en España. Busco un laboratorio que haga una prueba física para un estudio abierto sobre redes ópticas escritas con láser de femtosegundo en vidrio.

Ya es público: un estudio numérico prerregistrado; cuatro pruebas registradas para refutar sus propias afirmaciones (una retiró una ventaja energética); una revisión bibliográfica verificada; predicciones registradas de la pérdida a 1550 nm de guías de trinchera (revestimiento deprimido), fijadas antes de medir; y un dossier de fabricación.

Lo que pido: un piloto de unos tres chips con guías de trinchera rectas en cuatro longitudes (1-4 cm), escritas en el vidrio y con la receta que ustedes consideren mejor, y una medida de cut-back a 1550 nm. Opcionalmente, un cupón de cruces de guías en serie. No impongo parámetros de escritura.

A cambio: coautoría (roles CRediT acordados antes), datos en bruto y código abiertos, y una predicción registrada que sus datos pueden confirmar o refutar. Los resultados negativos se publican en las mismas condiciones.

Repositorio y dossier: https://github.com/Agnuxo1/Silice-Neuro3D-Cube (Docs/CIERRE-20261012/T28-FABRICATION-DOSSIER.md)

Si encaja con su grupo, o sabe a quién, le agradecería una breve respuesta.

Un saludo cordial,
Francisco Angulo de Lafuente
```

## Sources consulted

- Crossref REST API (all DOIs above), OpenAlex API (affiliations and Spanish-institution counts), arXiv abstracts 2401.03382, 2408.06688, 2609.16419, Europe PMC (Southampton abstract).
- Project files: `Docs/CIERRE-20261012/T28-FABRICATION-DOSSIER.md`, `T26-STATE-OF-THE-ART.md`, `T20-DECISION.md`, `H1-AMENDMENT-A1-20261013.md`, `RESUMEN-PARA-FRAN.md`, and `resultados/agent/t26_sota_20261012/records.json` (read only).
- GitHub API for `Agnuxo1/Silice-Neuro3D-Cube` (visibility, contents, compare).
- European Commission press release IP/22/1544 (4 March 2022) and reports of the fifth sanctions package (8 April 2022), via search.
- Official or company pages quoted in the entries (USAL ALF, IO-CSIC LPG, ULL portal, EPFL Galatea, Toronto Herman Group, Heriot-Watt PHI, Southampton ORC, ANFF, Modular Photonics, FEMTOprint, JOANNEUM RESEARCH, LightFab, Ephos, Lasers4EU, MSU QOT lab).
