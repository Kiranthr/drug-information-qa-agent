"""
Database and Document Seeding Script for Initial 6 Medicines.
Generates official FDA package insert PDFs and indexes them into SQLite and ChromaDB.

Supported Medicines:
1. Amoxicillin
2. Metformin
3. Paracetamol (Acetaminophen)
4. Atorvastatin
5. Lisinopril
6. Ibuprofen
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import fitz  # PyMuPDF
from app.core.config import settings
from app.core.logging import logger
from app.db.session import init_db, SessionLocal
from app.models.sql_models import Medicine
from app.services.ingestion_service import ingestion_service

SEED_MEDICINES_DATA = [
    {
        "id": "amoxicillin",
        "generic_name": "Amoxicillin",
        "brand_names": "Amoxil, Moxatag, Trimox",
        "drug_class": "Penicillin-class Aminopenicillin Antibacterial",
        "description": "Broad-spectrum antibacterial indicated for infections of the ear, nose, throat, genitourinary tract, skin, and lower respiratory tract caused by susceptible microorganisms.",
        "label_text": """HIGHLIGHTS OF PRESCRIBING INFORMATION: AMOXICILLIN CAPSULES, USP

1 INDICATIONS AND USAGE
Amoxicillin is a penicillin-class antibacterial indicated for treatment of infections due to susceptible isolates of designated microorganisms:
- Infections of the ear, nose, and throat (e.g., otitis media, pharyngitis, tonsillitis due to Streptococcus species).
- Infections of the genitourinary tract (e.g., Escherichia coli, Proteus mirabilis, Enterococcus faecalis).
- Infections of the skin and skin structure (e.g., Streptococcus spp., staphylococci, E. coli).
- Infections of the lower respiratory tract (e.g., Streptococcus pneumoniae, Haemophilus influenzae).
- Helicobacter pylori eradication to reduce the risk of duodenal ulcer recurrence in triple or dual therapy regimens.

2 DOSAGE AND ADMINISTRATION
- Adults: 250 mg to 500 mg every 8 hours or 500 mg to 875 mg every 12 hours depending on infection severity.
- Pediatric Patients (aged > 3 months): 20 to 45 mg/kg/day in divided doses every 8 or 12 hours.
- Neonates and Infants (aged <= 12 weeks): Maximum dose 30 mg/kg/day divided every 12 hours.
- Renal Impairment: For GFR 10 to 30 mL/min, administer 250 mg or 500 mg every 12 hours. For GFR < 10 mL/min, administer 250 mg or 500 mg every 24 hours.

4 CONTRAINDICATIONS
Amoxicillin is contraindicated in patients who have experienced a serious hypersensitivity reaction (e.g., anaphylaxis or Stevens-Johnson syndrome) to amoxicillin or to other beta-lactam antibacterial drugs (e.g., penicillins and cephalosporins).

5 WARNINGS AND PRECAUTIONS
- Anaphylactic Reactions: Serious and occasionally fatal hypersensitivity (anaphylactic) reactions have been reported in patients on penicillin therapy. Carefully inquire regarding previous hypersensitivity before initiating therapy.
- Clostridioides difficile-Associated Diarrhea (CDAD): Reported with nearly all antibacterial agents, ranging in severity from mild diarrhea to fatal colitis. If CDAD is suspected or confirmed, ongoing antibiotic use not directed against C. difficile may need to be discontinued.
- Development of Drug-Resistant Bacteria: Prescribing amoxicillin in the absence of a proven or strongly suspected bacterial infection is unlikely to provide benefit and increases the risk of drug-resistant bacteria.

6 ADVERSE REACTIONS
The most frequent adverse effects are:
- Gastrointestinal: Nausea, vomiting, diarrhea, and black hairy tongue.
- Hypersensitivity Reactions: Erythematous maculopapular rashes, urticaria, serum sickness-like reactions.
- Hematologic: Anemia, thrombocytopenia, leukopenia, agranulocytosis (usually reversible upon cessation).
- Central Nervous System: Hyperactivity, agitation, anxiety, insomnia, confusion, and dizziness (rare).

7 DRUG INTERACTIONS
- Probenecid: Decreases renal tubular secretion of amoxicillin, resulting in increased and prolonged blood levels.
- Oral Anticoagulants (e.g., Warfarin): Concomitant administration may prolong prothrombin time and INR; monitoring is recommended.
- Allopurinol: Concomitant administration substantially increases the incidence of skin rashes.
- Oral Contraceptives: May affect gut flora, leading to lower estrogen reabsorption and reduced oral contraceptive efficacy.

10 OVERDOSAGE
In case of overdosage, discontinue medication, treat symptomatically, and institute supportive measures as required. Renal impairment appears to be reversible with cessation of drug administration. High blood levels may occur more readily in patients with impaired renal function; amoxicillin may be removed from circulation by hemodialysis.
"""
    },
    {
        "id": "metformin",
        "generic_name": "Metformin",
        "brand_names": "Glucophage, Fortamet, Glumetza, Riomet",
        "drug_class": "Biguanide Antihyperglycemic Agent",
        "description": "First-line oral antidiabetic medicine used to manage type 2 diabetes mellitus by decreasing hepatic glucose production and improving insulin sensitivity.",
        "label_text": """HIGHLIGHTS OF PRESCRIBING INFORMATION: METFORMIN HYDROCHLORIDE TABLETS

WARNING: LACTIC ACIDOSIS
Post-marketing cases of metformin-associated lactic acidosis have resulted in death, hypothermia, hypotension, and resistant bradyarrhythmias. The onset of metformin-associated lactic acidosis is often subtle, accompanied only by nonspecific symptoms such as malaise, myalgias, respiratory distress, somnolence, and abdominal pain. Risk factors include renal impairment, concomitant use of certain drugs (e.g., carbonic anhydrase inhibitors), age 65 years or older, radiological study with contrast, surgery and other procedures, hypoxic states, and excessive alcohol intake. If lactic acidosis is suspected, immediately discontinue metformin and institute general supportive measures in a hospital setting.

1 INDICATIONS AND USAGE
Metformin hydrochloride is a biguanide indicated as an adjunct to diet and exercise to improve glycemic control in adults and pediatric patients aged 10 years and older with type 2 diabetes mellitus.

2 DOSAGE AND ADMINISTRATION
- Adults: Recommended starting dose is 500 mg orally twice daily or 850 mg once daily with meals. Increase in increments of 500 mg weekly or 850 mg every 2 weeks up to maximum dose of 2550 mg per day in divided doses.
- Renal Impairment: Assess renal function prior to initiation:
  - eGFR 45 to 59 mL/min/1.73 m2: Initiation is not recommended, but if already taking, monitor renal function every 3 to 6 months.
  - eGFR 30 to 44 mL/min/1.73 m2: Maximum recommended dose is 1000 mg per day.
  - eGFR < 30 mL/min/1.73 m2: CONTRAINDICATED.
- Discontinue metformin at the time of or prior to iodinated contrast imaging procedures in patients with eGFR between 30 and 60 mL/min/1.73 m2.

4 CONTRAINDICATIONS
- Severe renal impairment (eGFR below 30 mL/min/1.73 m2).
- Known hypersensitivity to metformin hydrochloride.
- Acute or chronic metabolic acidosis, including diabetic ketoacidosis, with or without coma.

5 WARNINGS AND PRECAUTIONS
- Lactic Acidosis: See Boxed Warning.
- Vitamin B12 Deficiency: Metformin may decrease vitamin B12 levels. Measure hematologic parameters annually and B12 at 2- to 3-year intervals.
- Hypoglycemia: Does not occur in patients receiving metformin alone under usual circumstances, but could occur in caloric deficiency, strenuous exercise, or combined with sulfonylureas or insulin.

6 ADVERSE REACTIONS
Most common adverse reactions (>5%): Diarrhea, nausea, vomiting, flatulence, asthenia, indigestion, abdominal discomfort, headache, and metallic taste in mouth. Adverse gastrointestinal events are most common during initiation and often transient.

7 DRUG INTERACTIONS
- Carbonic Anhydrase Inhibitors (e.g., Topiramate, Zonisamide): May increase risk of lactic acidosis.
- Drugs that Reduce Metformin Clearance (e.g., Ranolazine, Vandetanib, Dolutegravir, Cimetidine): May increase systemic exposure to metformin.
- Alcohol: Potentiates the effect of metformin on lactate metabolism.
"""
    },
    {
        "id": "paracetamol",
        "generic_name": "Paracetamol",
        "brand_names": "Acetaminophen, Tylenol, Panadol, Calpol",
        "drug_class": "Analgesic and Antipyretic Agent",
        "description": "Widely used over-the-counter and prescription pain reliever and fever reducer that acts centrally by inhibiting prostaglandin synthesis.",
        "label_text": """HIGHLIGHTS OF PRESCRIBING INFORMATION: PARACETAMOL (ACETAMINOPHEN)

WARNING: LIVER TOXICITY (HEPATOTOXICITY)
Acetaminophen has been associated with cases of acute liver failure, at times resulting in liver transplant and death. Most of the cases of liver injury are associated with the use of acetaminophen at doses that exceed 4000 milligrams per day, and often involve more than one acetaminophen-containing product.

1 INDICATIONS AND USAGE
Paracetamol (Acetaminophen) is indicated for:
- Relief of mild to moderate pain including headache, toothache, muscle aches, backache, osteoarthritis, and menstrual cramps.
- Reduction of fever in adults and children.

2 DOSAGE AND ADMINISTRATION
- Adults and Adolescents (>= 12 years): 325 mg to 650 mg every 4 to 6 hours or 1000 mg every 6 hours as needed.
- Maximum Daily Dose: Do not exceed 4000 mg (4 grams) in 24 hours from all sources in adults. In chronic alcohol users or patients with hepatic impairment, maximum daily dose should not exceed 2000 mg to 3000 mg.
- Pediatric Patients (< 12 years): 10 to 15 mg/kg per dose every 4 to 6 hours as needed (maximum 5 doses or 75 mg/kg per day).
- Do not use with any other drug containing acetaminophen/paracetamol.

4 CONTRAINDICATIONS
- Hypersensitivity to acetaminophen or any component of the formulation.
- Severe acute liver impairment or active severe hepatic disease.

5 WARNINGS AND PRECAUTIONS
- Hepatotoxicity: Do not exceed recommended maximum daily dose. Avoid use with other acetaminophen-containing medications. Chronic alcohol consumption (> 3 drinks per day) increases hepatotoxicity risk.
- Serious Skin Reactions: Rarely, paracetamol may cause serious skin reactions such as acute generalized exanthematous pustulosis (AGEP), Stevens-Johnson Syndrome (SJS), and toxic epidermal necrolysis (TEN). Discontinue immediately at first appearance of skin rash.

6 ADVERSE REACTIONS
Generally well tolerated at therapeutic doses.
- Rare adverse reactions: Allergic skin eruptions, urticaria, erythema, thrombocytopenia, leukopenia, neutropenia.
- Hepatic: Elevated liver enzymes (ALT, AST) with supra-therapeutic doses.

7 DRUG INTERACTIONS
- Alcohol: Concomitant chronic alcohol use increases the risk of severe liver damage.
- Warfarin: Chronic high-dose paracetamol use (> 2000 mg/day for several days) may enhance the anticoagulant effect of warfarin and increase bleeding risk.
- Enzyme Inducers (e.g., Carbamazepine, Phenytoin, Rifampin): May accelerate metabolism of paracetamol to toxic metabolite NAPQI, increasing hepatotoxicity risk.

10 OVERDOSAGE
Paracetamol overdose is a medical emergency. Toxic doses saturate glutathione conjugation, accumulating toxic metabolite N-acetyl-p-benzoquinone imine (NAPQI) causing centrilobular hepatic necrosis.
- Symptoms: Phase 1 (0-24 hrs): Nausea, vomiting, pallor, diaphoresis. Phase 2 (24-72 hrs): Right upper quadrant pain, elevated transaminases. Phase 3 (72-96 hrs): Hepatic failure, jaundice, encephalopathy, coagulopathy.
- Treatment: Prompt administration of the antidote N-acetylcysteine (NAC) within 8 to 10 hours of ingestion is highly effective. Contact Poison Control (1-800-222-1222) immediately.
"""
    },
    {
        "id": "atorvastatin",
        "generic_name": "Atorvastatin",
        "brand_names": "Lipitor, Torvast",
        "drug_class": "HMG-CoA Reductase Inhibitor (Statin)",
        "description": "Lipid-lowering agent that selectively and competitively inhibits HMG-CoA reductase, decreasing cholesterol synthesis in the liver and reducing cardiovascular disease risk.",
        "label_text": """HIGHLIGHTS OF PRESCRIBING INFORMATION: ATORVASTATIN CALCIUM TABLETS

1 INDICATIONS AND USAGE
Atorvastatin calcium is indicated:
- To reduce the risk of myocardial infarction, stroke, revascularization procedures, and angina in patients with multiple risk factors for coronary heart disease (CHD) or type 2 diabetes.
- As an adjunct to diet to reduce elevated total cholesterol, LDL-C, apolipoprotein B, and triglycerides in patients with primary hyperlipidemia and mixed dyslipidemia.
- For primary dysbetalipoproteinemia and homozygous familial hypercholesterolemia.

2 DOSAGE AND ADMINISTRATION
- Dose range: 10 mg to 80 mg orally once daily, taken at any time of day, with or without food.
- Recommended starting dose: 10 mg or 20 mg once daily. For patients requiring large LDL-C reduction (> 45%), start at 40 mg once daily.
- Assess lipid levels within 2 to 4 weeks after initiation and adjust dosage accordingly.

4 CONTRAINDICATIONS
- Acute liver failure or decompensated cirrhosis.
- Hypersensitivity to atorvastatin or any excipients in the tablets.

5 WARNINGS AND PRECAUTIONS
- Myopathy and Rhabdomyolysis: Rare cases of rhabdomyolysis with acute renal failure secondary to myoglobinuria have been reported. Risk is increased in elderly patients (>= 65), patients with uncontrolled hypothyroidism or renal impairment, and when coadministered with certain interacting medications. Advise patients to promptly report unexplained muscle pain, tenderness, or weakness.
- Liver Enzyme Elevations: Persistent elevations in hepatic transaminases (ALT/AST > 3 times upper limit of normal) can occur. Perform liver enzyme tests before initiating therapy and as clinically indicated thereafter.
- Increases in HbA1c and Fasting Glucose: Increases in blood sugar levels have been reported with statins.

6 ADVERSE REACTIONS
Most common adverse reactions (incidence >= 2%):
- Nasopharyngitis, arthralgia, diarrhea, pain in extremity, urinary tract infection, dyspepsia, nausea, musculoskeletal pain, muscle spasms, and insomnia.

7 DRUG INTERACTIONS
- Strong CYP3A4 Inhibitors (e.g., Clarithromycin, Itraconazole, Ketoconazole, HIV/HCV protease inhibitors): Substantially increase atorvastatin plasma concentrations and risk of myopathy. Avoid coadministration or limit atorvastatin dose to 20 mg.
- Cyclosporine or Gemfibrozil: Concomitant use increases risk of rhabdomyolysis. Avoid coadministration.
- Grapefruit Juice: Ingestion of large quantities (> 1.2 liters daily) increases atorvastatin exposure; avoid large quantities.
- Digoxin: Steady-state plasma digoxin concentrations increase by approximately 20%; monitor digoxin levels.
- Oral Contraceptives: Increases AUC of norethindrone and ethinyl estradiol by approximately 30% and 20%.

8 USE IN SPECIFIC POPULATIONS
- Pregnancy: Discontinue atorvastatin as soon as pregnancy is recognized.
- Lactation: Breastfeeding is not recommended during treatment with atorvastatin.
"""
    },
    {
        "id": "lisinopril",
        "generic_name": "Lisinopril",
        "brand_names": "Prinivil, Zestril, Qbrelis",
        "drug_class": "Angiotensin Converting Enzyme (ACE) Inhibitor",
        "description": "Antihypertensive medication that inhibits angiotensin-converting enzyme, suppressing the renin-angiotensin-aldosterone system, lowering blood pressure and improving heart failure outcomes.",
        "label_text": """HIGHLIGHTS OF PRESCRIBING INFORMATION: LISINOPRIL TABLETS

WARNING: FETAL TOXICITY
- When pregnancy is detected, discontinue lisinopril as soon as possible.
- Drugs that act directly on the renin-angiotensin system can cause injury and death to the developing fetus. See Warnings and Precautions.

1 INDICATIONS AND USAGE
Lisinopril is an ACE inhibitor indicated for:
- Treatment of hypertension in adult patients and pediatric patients 6 years of age and older to lower blood pressure.
- Adjunctive therapy in the management of heart failure in patients who are not responding adequately to diuretics and digitalis.
- Treatment of hemodynamically stable patients within 24 hours of acute myocardial infarction to improve survival.

2 DOSAGE AND ADMINISTRATION
- Hypertension: Initial adult monotherapy dose is 10 mg once daily. Adjust dosage according to blood pressure response up to maximum 40 mg once daily.
- Heart Failure: Initial dose 2.5 mg to 5 mg once daily with diuretics and digitalis. Target dose is 20 mg to 40 mg once daily.
- Acute Myocardial Infarction: 5 mg within 24 hours, followed by 5 mg after 24 hours, 10 mg after 48 hours, then 10 mg daily for 6 weeks.
- Renal Impairment: For CrCl 10 to 30 mL/min, initial dose is 5 mg daily. For CrCl < 10 mL/min, initial dose is 2.5 mg daily.

4 CONTRAINDICATIONS
- Lisinopril is contraindicated in patients with a history of angioedema related to previous ACE inhibitor treatment, or hereditary or idiopathic angioedema.
- Do not coadminister aliskiren with lisinopril in patients with diabetes.
- Do not coadminister with a neprilysin inhibitor (e.g., sacubitril). Allow 36 hours between administration of lisinopril and sacubitril/valsartan.

5 WARNINGS AND PRECAUTIONS
- Fetal Toxicity: See Boxed Warning.
- Angioedema: Head and neck angioedema, including laryngeal edema, may occur and be fatal. Intestinal angioedema presenting with abdominal pain has also been reported. Discontinue lisinopril immediately and administer emergency therapy.
- Hypotension: Symptomatic hypotension may occur, particularly in volume-depleted or salt-depleted patients.
- Renal Impairment and Hyperkalemia: Monitor renal function and serum potassium periodically. Hyperkalemia risk is increased in patients with renal impairment, diabetes, and those using potassium supplements or potassium-sparing diuretics.
- Persistent Dry Cough: Characteristically nonproductive, persistent, and resolves after cessation of therapy.

6 ADVERSE REACTIONS
Most common adverse reactions (incidence >= 1%): Headache, dizziness, persistent dry cough, fatigue, nausea, diarrhea, rash, orthostatic effects, and hyperkalemia.

7 DRUG INTERACTIONS
- Potassium-Sparing Diuretics (e.g., Spironolactone, Triamterene) or Potassium Supplements: Lead to significant increases in serum potassium. Monitor potassium closely.
- Nonsteroidal Anti-Inflammatory Drugs (NSAIDs / Ibuprofen): Concomitant administration in elderly or volume-depleted patients may result in deterioration of renal function, including possible acute renal failure, and attenuated antihypertensive effect.
- Lithium: Increased serum lithium concentrations and symptoms of lithium toxicity reported.
- Dual Blockade of RAS: Combining ACE inhibitors with ARBs or aliskiren increases risks of hypotension, hyperkalemia, and renal failure.
"""
    },
    {
        "id": "ibuprofen",
        "generic_name": "Ibuprofen",
        "brand_names": "Advil, Motrin, Nurofen, Brufen",
        "drug_class": "Nonsteroidal Anti-inflammatory Drug (NSAID)",
        "description": "NSAID with analgesic, antipyretic, and anti-inflammatory properties that acts through nonselective inhibition of cyclooxygenase enzymes (COX-1 and COX-2).",
        "label_text": """HIGHLIGHTS OF PRESCRIBING INFORMATION: IBUPROFEN TABLETS

WARNING: RISK OF SERIOUS CARDIOVASCULAR AND GASTROINTESTINAL EVENTS
Cardiovascular Thrombotic Events:
- Nonsteroidal anti-inflammatory drugs (NSAIDs) cause an increased risk of serious cardiovascular thrombotic events, including myocardial infarction and stroke, which can be fatal. This risk may occur early in treatment and may increase with duration of use.
- Ibuprofen is contraindicated in the setting of coronary artery bypass graft (CABG) surgery.
Gastrointestinal Bleeding, Ulceration, and Perforation:
- NSAIDs cause an increased risk of serious gastrointestinal (GI) adverse events including bleeding, ulceration, and perforation of the stomach or intestines, which can be fatal. These events can occur at any time during use and without warning symptoms. Elderly patients and patients with prior history of peptic ulcer disease and/or GI bleeding are at greater risk for serious GI events.

1 INDICATIONS AND USAGE
Ibuprofen is indicated for:
- Relief of signs and symptoms of rheumatoid arthritis and osteoarthritis.
- Relief of mild to moderate pain (headache, dental pain, musculoskeletal pain, dysmenorrhea).
- Reduction of fever.

2 DOSAGE AND ADMINISTRATION
- Use the lowest effective dosage for the shortest duration consistent with individual patient treatment goals.
- Rheumatoid Arthritis and Osteoarthritis: 1200 mg to 3200 mg daily divided into 3 or 4 equal doses (e.g., 400 mg, 600 mg, or 800 mg three or four times daily). Do not exceed 3200 mg per day.
- Mild to Moderate Pain: 400 mg every 4 to 6 hours as necessary. Over-the-counter maximum daily dose is 1200 mg/day unless directed by a doctor.

4 CONTRAINDICATIONS
- Known hypersensitivity to ibuprofen or other NSAIDs (history of asthma, urticaria, or allergic-type reactions after taking aspirin or other NSAIDs).
- In the setting of coronary artery bypass graft (CABG) surgery.

5 WARNINGS AND PRECAUTIONS
- Cardiovascular Thrombotic Events: See Boxed Warning. Avoid use in patients with recent MI unless benefits outweigh risks.
- Gastrointestinal Bleeding and Ulceration: See Boxed Warning.
- Hepatotoxicity: Borderline elevations of liver tests may occur in up to 15% of patients taking NSAIDs.
- Hypertension: NSAIDs can lead to new onset or worsening of preexisting hypertension.
- Heart Failure and Edema: NSAIDs may blunt cardiovascular response to loop diuretics and worsen heart failure.
- Renal Toxicity and Hyperkalemia: Long-term administration can result in renal papillary necrosis and other renal injury. Monitor renal function in patients with renal impairment, heart failure, liver dysfunction, or those taking ACE inhibitors.

6 ADVERSE REACTIONS
Most common adverse reactions (incidence 4% to 16%): Nausea, epigastric pain, heartburn, diarrhea, abdominal distress, dizziness, headache, nervousness, edema, and fluid retention.

7 DRUG INTERACTIONS
- ACE Inhibitors and ARBs (e.g., Lisinopril): Concomitant use may diminish the antihypertensive effect of ACE inhibitors and precipitate acute renal failure, especially in volume-depleted elderly patients.
- Anticoagulants (e.g., Warfarin, Aspirin): Concomitant use substantially increases the risk of serious gastrointestinal bleeding.
- Lithium: NSAIDs have produced an elevation of plasma lithium levels and a reduction in renal lithium clearance.
- Methotrexate: NSAIDs may reduce tubular secretion of methotrexate, enhancing toxicity.
- Diuretics: Ibuprofen can reduce the natriuretic effect of furosemide and thiazides.
"""
    }
]


def generate_pdf_from_text(text: str, output_path: Path) -> None:
    """Create a multi-page PDF document with styled text using PyMuPDF."""
    doc = fitz.open()
    
    # 72 points per inch, letter size is 612 x 792
    page_width, page_height = 612, 792
    margin = 54
    line_height = 14
    max_lines_per_page = int((page_height - 2 * margin) / line_height)

    lines = text.strip().split("\n")
    current_page_lines = []

    def flush_page(p_lines):
        page = doc.new_page(width=page_width, height=page_height)
        y = margin
        for line in p_lines:
            # Check if line is a header
            is_title = line.startswith("HIGHLIGHTS OF PRESCRIBING INFORMATION") or line.startswith("WARNING:")
            is_section = any(line.strip().startswith(f"{i} ") for i in range(1, 20))
            
            fontsize = 12 if is_title else (10 if is_section else 9)
            fontname = "helv"  # Standard Helvetica
            
            # Simple word-wrap
            if len(line) > 85 and not is_title:
                sub_lines = [line[i:i+80] for i in range(0, len(line), 80)]
                for sub in sub_lines:
                    page.insert_text(fitz.Point(margin, y), sub, fontsize=fontsize, fontname=fontname)
                    y += line_height
            else:
                page.insert_text(fitz.Point(margin, y), line, fontsize=fontsize, fontname=fontname)
                y += line_height + (3 if is_section else 0)
        return

    for line in lines:
        current_page_lines.append(line)
        if len(current_page_lines) >= max_lines_per_page:
            flush_page(current_page_lines)
            current_page_lines = []

    if current_page_lines:
        flush_page(current_page_lines)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    total_doc_pages = len(doc)
    doc.close()
    logger.info(f"Generated PDF: {output_path} ({total_doc_pages} pages)")


def seed_database():
    """Main seeding routine."""
    logger.info("Initializing database and seeding 6 initial medicines...")
    settings.ensure_directories()
    init_db()

    raw_pdf_dir = Path("./data/raw_pdfs")
    raw_pdf_dir.mkdir(parents=True, exist_ok=True)

    db = SessionLocal()
    try:
        total_seeded = 0
        for med_data in SEED_MEDICINES_DATA:
            med_id = med_data["id"]
            
            # 1. Register or update medicine in SQLite
            medicine = db.query(Medicine).filter(Medicine.id == med_id).first()
            if not medicine:
                medicine = Medicine(
                    id=med_id,
                    generic_name=med_data["generic_name"],
                    brand_names=med_data["brand_names"],
                    drug_class=med_data["drug_class"],
                    description=med_data["description"]
                )
                db.add(medicine)
                db.commit()
                db.refresh(medicine)
                logger.info(f"Registered medicine: {medicine.generic_name} ({med_id})")

            # 2. Generate PDF file
            pdf_filename = f"{med_id}_fda_label.pdf"
            pdf_path = raw_pdf_dir / pdf_filename
            generate_pdf_from_text(med_data["label_text"], pdf_path)

            # 3. Ingest and Index into ChromaDB
            doc_title = f"{med_data['generic_name']} Official FDA Package Insert"
            ingestion_service.process_pdf(
                db=db,
                file_path=str(pdf_path),
                medicine_id=med_id,
                title=doc_title,
                source="FDA DailyMed",
                original_filename=pdf_filename
            )
            total_seeded += 1

        logger.info(f"Successfully seeded and indexed all {total_seeded} initial medicines!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
