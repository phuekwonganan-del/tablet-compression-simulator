# tablet-compression-simulator
QbD-based tablet compression simulator              with physics engine and defect prediction
# 💊 Pharmaceutical Tablet Compression Simulator

QbD-based tablet compression simulator
built with Python + Streamlit

## Author
Tok | Pharmacy Year 4 | Thammasat University

## Modules
| Module | Description |
|--------|-------------|
| physics_engine | Heckel + Ryshkewitch + Fell-Newton |
| machine_module | Single Punch + Rotary Press |
| excipient_database | 5 excipients with flow properties |
| defect_predictor | Capping/Lamination/Sticking/Twinning |
| animation_module | Real-time interactive animation |

## Run
pip install streamlit matplotlib numpy
streamlit run app.py

## References
- Heckel RW (1961)
- Ryshkewitch E (1953)
- Fell JT, Newton JM (1970)
- USP <1217> Tablet Breaking Force
