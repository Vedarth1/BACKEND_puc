word_set ={
    "IND",
    " ",
    "-",
    "_",
     "MARUTI SUZUKI",
    "HYUNDAI",
    "TATA MOTORS",
    "MAHINDRA & MAHINDRA",
    "TOYOTA",
    "HONDA",
    "FORD",
    "RENAULT",
    "NISSAN",
    "VOLKSWAGEN",
    "MERCEDES-BENZ",
    "BMW",
    "AUDI",
    "SKODA",
    "VOLVO",
    "JEEP",
    "KIA",
    "MG MOTOR",
    "JAGUAR LAND ROVER",
    "FIAT",
    "LAMBORGHINI",
    "PORSCHE",
    "ROLLS-ROYCE",
    "BENTLEY",
    "ASTON MARTIN",
    "FERRARI",
    "MASERATI",
    "ISUZU",
    "FORCE MOTORS",
    "PREMIER",
    "BAJAJ AUTO",
    "TVS MOTORS",
    "HERO MOTOCORP",
    "ROYAL ENFIELD",
    "MAHINDRA TWO WHEELERS",
    "YAMAHA",
    "SUZUKI MOTORCYCLE",
    "KAWASAKI",
    "TRIUMPH MOTORCYCLES",
    "HARLEY-DAVIDSON",
    "HYOSUNG",
    "INDIAN MOTORCYCLE",
    "PIAGGIO",
    "DUCATI",
    "APRILIA",
    "BENELLI",
    "MV AGUSTA",
    "NORTON",
    "HUSQVARNA",
    "BMW MOTORRAD",
    "KTM",
    "JAWA",
    "TRIUMPH MOTORCYCLES",
    "KYMCO",
    "OLA ELECTRIC",
}

def parse_rc_number(extracted_text):
    resultarr=[]
    for extractedtext in extracted_text:
        text_blocks = extractedtext.split('\n')
        result = ""
        for text in text_blocks:
            if text not in word_set and len(text) >= 2 and len(text)<=10:
                result += text
        result = result.replace(" ", "")
        result = result.replace(".", "")
        print(result)
        resultarr.append(result)
        
    return resultarr