# Dynamics

Kepler's third law uses SI constants and returns AU/day quantities through explicit conversion. Adjacent spacing uses the mutual Hill radius

\[ R_{H,m} = \frac{a_1+a_2}{2}\left(\frac{m_1+m_2}{3M_*}\right)^{1/3}, \qquad \Delta = \frac{a_2-a_1}{R_{H,m}}. \]

Angular Momentum Deficit is implemented as \(\sum m_i\sqrt{a_i}[1-\sqrt{1-e_i^2}\cos i_i]\) in a common proportional unit. Hill spacing and AMD are diagnostics, not general proofs of stability.

WHFast is the long-term default for well-separated nearly Keplerian configurations; IAS15 is available for adaptive high-accuracy work. MEGNO can be calculated for selected systems, but no release-wide chaos classification is claimed yet.

