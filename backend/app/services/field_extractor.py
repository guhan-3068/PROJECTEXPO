import re
from typing import Dict, List, Any, Optional, Tuple
from app.utils.dates import parse_date_string

Tuple_str_confidence = Tuple[str, float]

def mask_sensitive_value(key: str, val: str) -> str:
    """
    Masks sensitive personal identifiers according to privacy guidelines:
    - Aadhaar: XXXX-XXXX-1234
    - PAN: AB***4F
    - Bank Account: ******1234
    """
    if not val:
        return val
    cleaned = val.strip()
    key_low = (key or "").lower()
    digits_only = re.sub(r"\D", "", cleaned)
    
    # 1. Bank Account masking
    if "account" in key_low or "bank" in key_low:
        if len(digits_only) >= 8:
            return f"******{digits_only[-4:]}"

    # 2. Aadhaar masking (12 digits)
    if "aadhaar" in key_low or (len(digits_only) == 12 and (key_low in ("doc_number", "id_number") or " " in cleaned)):
        if len(digits_only) == 12:
            return f"XXXX-XXXX-{digits_only[-4:]}"
    
    # 3. PAN masking (5 letters + 4 digits + 1 letter)
    pan_match = re.match(r"^([A-Z]{5})([0-9]{4})([A-Z])$", cleaned.upper())
    if pan_match:
        return f"{pan_match.group(1)[:2]}***{pan_match.group(2)[-1:]}{pan_match.group(3)}"

    return cleaned

class FieldExtractor:
    """
    Intelligent field extraction and document classification service
    specialized for Indian Citizen Services & General Identity Verification.
    """

    DOCUMENT_SIGNATURES = {
        "AADHAAR": [
            r"aadhaar", r"uidai", r"unique\s*identification\s*authority",
            r"government\s*of\s*india", r"bharat\s*sarkar",
            r"mera\s*aadhaar", r"enrollment\s*no", r"\b\d{4}\s\d{4}\s\d{4}\b",
            r"help@uidai\.gov\.in", r"vid\s*[:\s]*\d{4}"
        ],
        "PAN_CARD": [
            r"permanent\s*account\s*number", r"income\s*tax\s*department",
            r"govt\.\s*of\s*india", r"\b[a-z]{5}[0-9]{4}[a-z]\b",
            r"father'?s?\s*name", r"pan\s*card", r"taxpayer"
        ],
        "RATION_CARD": [
            r"ration\s*card", r"smart\s*family\s*card", r"family\s*card",
            r"civil\s*supplies", r"consumer\s*protection", r"pds",
            r"tnepds", r"fair\s*price\s*shop", r"commodit(?:y|ies)",
            r"head\s*of\s*family", r"nfsa"
        ],
        "NATIVITY_CERTIFICATE": [
            r"nativity\s*certificate", r"certificate\s*of\s*nativity",
            r"resident\s*of\s*tamil\s*nadu", r"permanent\s*resident",
            r"tahsildar", r"revenue\s*department", r"revenue\s*divisional",
            r"e-sevai", r"esevai", r"native\s*of"
        ],
        "COMMUNITY_CERTIFICATE": [
            r"community\s*certificate", r"caste\s*certificate",
            r"scheduled\s*caste", r"scheduled\s*tribe", r"backward\s*class",
            r"most\s*backward", r"obc", r"mbc", r"sc\s*/\s*st",
            r"revenue\s*department", r"tahsildar", r"caste\s*verification"
        ],
        "INCOME_CERTIFICATE": [
            r"income\s*certificate", r"annual\s*income", r"gross\s*income",
            r"rupees\s*per\s*annum", r"revenue\s*department", r"tahsildar",
            r"source\s*of\s*income", r"e-sevai", r"family\s*income"
        ],
        "FIRST_GRADUATE_CERTIFICATE": [
            r"first\s*graduate", r"first\s*generation\s*graduate",
            r"no\s*graduate\s*in\s*family", r"higher\s*education\s*tuition\s*fee",
            r"directorate\s*of\s*technical\s*education", r"tahsildar"
        ],
        "TRANSFER_CERTIFICATE": [
            r"transfer\s*certificate", r"school\s*transfer", r"college\s*transfer",
            r"t\.c\.", r"\btc\b", r"date\s*of\s*leaving", r"conduct\s*and\s*character",
            r"headmaster", r"principal", r"admission\s*no"
        ],
        "EDUCATIONAL_CERTIFICATE": [
            r"mark\s*sheet", r"mark\s*statement", r"higher\s*secondary",
            r"sslc", r"hsc", r"secondary\s*school", r"cbse", r"icse",
            r"board\s*of\s*secondary", r"degree\s*certificate",
            r"provisional\s*certificate", r"semester", r"roll\s*no",
            r"register\s*no", r"cgpa", r"total\s*marks"
        ],
        "DRIVING_LICENSE": [
            r"driver'?s?\s*licen[sc]e", r"driving\s*licen[sc]e", r"dl\s*no",
            r"motor\s*vehicles?\s*act", r"licensing\s*authority",
            r"transport\s*department", r"parivahan", r"form\s*7", r"rto"
        ],
        "VOTER_ID": [
            r"election\s*commission\s*of\s*india", r"electoral\s*photo\s*identity",
            r"voter\s*id", r"epic\s*no", r"parliamentary\s*constituency",
            r"assembly\s*constituency"
        ],
        "BIRTH_CERTIFICATE": [
            r"birth\s*certificate", r"certificate\s*of\s*birth",
            r"registration\s*of\s*birth", r"name\s*of\s*child",
            r"municipal\s*corporation", r"registrar\s*of\s*birth"
        ],
        "DEATH_CERTIFICATE": [
            r"death\s*certificate", r"certificate\s*of\s*death",
            r"date\s*of\s*death", r"cause\s*of\s*death", r"registration\s*of\s*death"
        ],
        "BANK_PASSBOOK": [
            r"bank\s*passbook", r"account\s*holder", r"account\s*number",
            r"ifsc\s*code", r"bank\s*statement", r"branch\s*code",
            r"state\s*bank", r"canara\s*bank", r"indian\s*bank",
            r"punjab\s*national", r"hdfc", r"icici"
        ],
        "DISABILITY_CERTIFICATE": [
            r"disability\s*certificate", r"unique\s*disability\s*id",
            r"udid", r"medical\s*board", r"percentage\s*of\s*disability",
            r"locomotor", r"visual\s*impairment"
        ],
        "BONAFIDE_CERTIFICATE": [
            r"bonafide\s*certificate", r"student\s*bonafide",
            r"bonafide\s*student", r"studying\s*in\s*our\s*institution",
            r"academic\s*year"
        ],
        "PASSPORT": [
            r"passport", r"republic\s*of\s*india", r"travel\s*document",
            r"p<ind", r"nationality\s*ind", r"issuing\s*authority"
        ],
        "RESIDENCE_CERTIFICATE": [
            r"residence\s*certificate", r"domicile\s*certificate",
            r"certificate\s*of\s*residence", r"proof\s*of\s*residence"
        ],
        "SCHOLARSHIP_DOCUMENTS": [
            r"scholarship", r"post\s*matric", r"national\s*scholarship\s*portal",
            r"sanction\s*order", r"welfare\s*scholarship"
        ],
        "APPLICATION_FORM": [
            r"application\s*form", r"applicant\s*signature", r"official\s*use",
            r"declaration", r"checklist", r"form\s*49a"
        ],
        "UTILITY_BILL": [
            r"utility\s*bill", r"electric", r"water\s*board", r"gas\s*bill",
            r"telecom", r"meter\s*no", r"billing\s*period", r"consumer\s*no",
            r"electricity\s*bill", r"eb\s*bill", r"tangedco", r"tneb",
            r"water\s*tax", r"property\s*tax", r"consumer\s*account"
        ]
    }

    def classify_document(self, text: str, user_claimed_category: Optional[str] = None) -> Tuple_str_confidence:
        """
        Classifies document based on weighted term matches and regular expressions.
        """
        lower = text.lower()
        scores = {}

        for doc_type, patterns in self.DOCUMENT_SIGNATURES.items():
            matches = sum(1 for p in patterns if re.search(p, lower))
            if matches > 0:
                scores[doc_type] = matches / len(patterns)

        if not scores:
            if user_claimed_category and user_claimed_category != "UNKNOWN":
                return user_claimed_category, 0.70
            return "UNKNOWN", 0.30

        best_category = max(scores, key=scores.get)
        confidence = round(min(scores[best_category] * 1.8, 0.98), 2)

        # Respect user claimed category if it has positive indicators
        if user_claimed_category and user_claimed_category in scores and scores[user_claimed_category] > 0.2:
            return user_claimed_category, round(max(confidence, 0.88), 2)

        return best_category, confidence

    def extract_fields(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts structured fields:
        - full_name
        - dob (Date of Birth)
        - doc_number (Masked identifier / Certificate number)
        - issue_date
        - expiry_date
        - address
        - father_name
        """
        fields = []

        # 1. Full Name
        name_val, name_conf = self._extract_name(text)
        if name_val:
            fields.append({
                "field_key": "full_name",
                "raw_value": name_val,
                "normalized_value": name_val.title(),
                "confidence": name_conf,
                "notes": "Extracted applicant/holder name"
            })

        # 2. Date of Birth
        dob_raw, dob_conf = self._extract_dob(text)
        if dob_raw:
            parsed_dob = parse_date_string(dob_raw)
            fields.append({
                "field_key": "dob",
                "raw_value": dob_raw,
                "normalized_value": parsed_dob.isoformat() if parsed_dob else dob_raw,
                "confidence": dob_conf if parsed_dob else 0.50,
                "notes": "Date of Birth"
            })

        # 3. Document / Certificate / ID Number (with privacy masking)
        doc_no, doc_conf = self._extract_doc_number(text)
        if doc_no:
            masked_no = mask_sensitive_value("doc_number", doc_no)
            fields.append({
                "field_key": "doc_number",
                "raw_value": masked_no,
                "normalized_value": masked_no,
                "confidence": doc_conf,
                "notes": "Document identifier / Certificate number (Masked for privacy)"
            })

        # 4. Father / Guardian Name
        father_val, father_conf = self._extract_father_name(text)
        if father_val:
            fields.append({
                "field_key": "father_name",
                "raw_value": father_val,
                "normalized_value": father_val.title(),
                "confidence": father_conf,
                "notes": "Father / Guardian name"
            })

        # 5. Expiry Date (STRICT: zero hallucination)
        expiry_raw, exp_conf = self._extract_expiry_date(text)
        if expiry_raw:
            parsed_exp = parse_date_string(expiry_raw)
            fields.append({
                "field_key": "expiry_date",
                "raw_value": expiry_raw,
                "normalized_value": parsed_exp.isoformat() if parsed_exp else expiry_raw,
                "confidence": exp_conf if parsed_exp else 0.50,
                "notes": "Document validity expiration date"
            })

        # 6. Issue Date
        issue_raw, iss_conf = self._extract_issue_date(text)
        if issue_raw:
            parsed_issue = parse_date_string(issue_raw)
            fields.append({
                "field_key": "issue_date",
                "raw_value": issue_raw,
                "normalized_value": parsed_issue.isoformat() if parsed_issue else issue_raw,
                "confidence": iss_conf if parsed_issue else 0.50,
                "notes": "Document date of issue / certification"
            })

        # 7. Address
        addr, addr_conf = self._extract_address(text)
        if addr:
            fields.append({
                "field_key": "address",
                "raw_value": addr,
                "normalized_value": addr,
                "confidence": addr_conf,
                "notes": "Residential address"
            })

        return fields

    def _extract_name(self, text: str) -> Tuple_str_confidence:
        patterns = [
            r"(?:Full\s*Name|Applicant\s*Name|Candidate\s*Name|Student\s*Name|Holder'?s?\s*Name|Name\s*of\s*the\s*Applicant|Name\s*of\s*the\s*Candidate|Name\s*of\s*the\s*Student|Name\s*of\s*the\s*Person|Name)\s*[:\-]\s*([A-Za-z .'-]{2,45})",
            r"(?:Surname\s*[:\-]\s*([A-Za-z .'-]{2,30})\s*(?:Given\s*Name[s]?\s*[:\-]\s*([A-Za-z .'-]{2,30})))",
            r"(?:This\s*is\s*to\s*certify\s*that\s*(?:Thiru|Tmt|Selvi|Mr\.|Ms\.|Shri|Smt\.)?\s*([A-Za-z .'-]{3,40}))",
            r"(?:Certified\s*that\s*(?:Selvan|Selvi|Mr\.|Ms\.)?\s*([A-Za-z .'-]{3,40}))"
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                if len(m.groups()) == 2 and m.group(1) and m.group(2):
                    return f"{m.group(2).strip()} {m.group(1).strip()}", 0.92
                val = m.group(1).split("\n")[0].split("\r")[0].strip()
                # filter out false positives
                low = val.lower()
                if not any(w in low for w in ["passport", "republic", "driving", "licence", "date", "birth", "signature", "certificate", "government", "tamil nadu", "department", "board"]):
                    return val, 0.90

        # Pattern 2: MRZ Line format P<IND...
        mrz_match = re.search(r"P<[A-Z]{3}([A-Z]+)<<([A-Z<]+)", text)
        if mrz_match:
            surname = mrz_match.group(1).replace("<", " ").strip()
            given = mrz_match.group(2).replace("<", " ").strip()
            return f"{given} {surname}", 0.95

        return "", 0.0

    def _extract_father_name(self, text: str) -> Tuple_str_confidence:
        patterns = [
            r"(?:Father'?s?\s*Name|Father\s*Name|Parent'?s?\s*Name|Guardian'?s?\s*Name|S/o|D/o|W/o)\s*[:\-]\s*([A-Za-z .'-]{2,40})",
            r"(?:Son\s*of|Daughter\s*of)\s*(?:Thiru|Shri|Mr\.)?\s*([A-Za-z .'-]{2,40})"
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                val = m.group(1).split("\n")[0].split("\r")[0].strip()
                if not any(w in val.lower() for w in ["date", "birth", "address", "signature", "village", "taluk"]):
                    return val, 0.88
        return "", 0.0

    def _extract_dob(self, text: str) -> Tuple_str_confidence:
        patterns = [
            r"(?:Date\s*of\s*Birth|DOB|Birth\s*Date|D\.O\.B\.|Born\s*on)\s*[:\-]?\s*([0-9]{1,4}[-/.][0-9A-Za-z]{1,9}[-/.][0-9]{2,4})",
            r"(?:Year\s*of\s*Birth|YOB)\s*[:\-]?\s*([0-9]{4})"
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip(), 0.92
        return "", 0.0

    def _extract_doc_number(self, text: str) -> Tuple_str_confidence:
        # 1. Aadhaar (12 digits, often formatted as 4-4-4)
        aadhaar_match = re.search(r"\b([0-9]{4}\s[0-9]{4}\s[0-9]{4})\b", text)
        if aadhaar_match:
            return aadhaar_match.group(1).strip(), 0.95

        # 2. PAN (5 uppercase letters, 4 digits, 1 uppercase letter)
        pan_match = re.search(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b", text)
        if pan_match:
            return pan_match.group(1).strip(), 0.95

        # 3. Driving License
        dl_match = re.search(r"(?:Licen[sc]e\s*No\.?|DL\s*No\.?)\s*[:\-]?\s*([A-Z0-9 -]{5,20})", text, re.IGNORECASE)
        if dl_match:
            return dl_match.group(1).strip(), 0.92

        # 4. Voter ID / EPIC
        epic_match = re.search(r"\b([A-Z]{3}[0-9]{7})\b", text)
        if epic_match:
            return epic_match.group(1).strip(), 0.92

        # 5. Ration / Family Card
        ration_match = re.search(r"(?:Card\s*No\.?|Ration\s*Card\s*No\.?|Family\s*Card\s*No\.?)\s*[:\-]?\s*([0-9]{2}/[A-Z0-9]+/[0-9]+|[A-Z0-9/-]{8,20})", text, re.IGNORECASE)
        if ration_match:
            return ration_match.group(1).strip(), 0.90

        # 6. Certificate / Register / TC / Roll Number
        cert_patterns = [
            r"(?:Certificate\s*No\.?|Cert\s*No\.?|Application\s*No\.?)\s*[:\-]?\s*([A-Z0-9/-]{6,25})",
            r"(?:Register\s*No\.?|Reg\s*No\.?|Roll\s*No\.?)\s*[:\-]?\s*([A-Z0-9]{5,16})",
            r"(?:T\.?C\.?\s*No\.?|Transfer\s*Cert\s*No\.?)\s*[:\-]?\s*([A-Z0-9/-]{4,20})",
            r"(?:Passport\s*No\.?|Passport\s*Number)\s*[:\-]?\s*([A-Z0-9]{6,12})"
        ]
        for p in cert_patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip(), 0.90

        return "", 0.0

    def _extract_expiry_date(self, text: str) -> Tuple_str_confidence:
        patterns = [
            r"(?:Date\s*of\s*Expiry|Expiry\s*Date|Expires\s*On|Valid\s*(?:Until|Thru|To|Upto)|Expiration\s*Date|EXP)\s*[:\-]?\s*([0-9]{1,4}[-/.][0-9A-Za-z]{1,9}[-/.][0-9]{2,4})"
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip(), 0.93
        return "", 0.0

    def _extract_issue_date(self, text: str) -> Tuple_str_confidence:
        patterns = [
            r"(?:Date\s*of\s*Issue|Issue\s*Date|Issued\s*On|Date\s*Issued|ISS|Certified\s*On|Date\s*of\s*Certification)\s*[:\-]?\s*([0-9]{1,4}[-/.][0-9A-Za-z]{1,9}[-/.][0-9]{2,4})"
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip(), 0.91
        return "", 0.0

    def _extract_address(self, text: str) -> Tuple_str_confidence:
        m = re.search(r"(?:Address|Residential\s*Address|Billing\s*Address|Native\s*Address|Permanent\s*Address)\s*[:\-]\s*([^\n\r]{10,120})", text, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            return val, 0.85
        return "", 0.0

field_extractor = FieldExtractor()
