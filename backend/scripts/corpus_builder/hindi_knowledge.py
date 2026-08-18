"""Multilingual Hindi and Hinglish Domain Knowledge Generator.
Authoritative, high-value bilingual Hindi technical and scientific documentation with natural Hindi and Hinglish phrasing.
"""
from __future__ import annotations

def get_hindi_documents() -> list[dict]:
    data = [
        # --- 1. GENERAL SCIENCE IN HINDI ---
        ("science-photosynthesis-hi", "प्रकाश संश्लेषण (Photosynthesis in Plants)", "general_science", "biology",
         "प्रकाश संश्लेषण (Photosynthesis / Photosynthesis kya hota hai) वह जैविक प्रक्रिया है जिसके द्वारा हरे पौधे, शैवाल और सायनोबैक्टीरिया सूर्य के प्रकाश की ऊर्जा को रासायनिक ऊर्जा में परिवर्तित करते हैं। पत्तियों के क्लोरोप्लास्ट में मौजूद क्लोरोफिल सूर्य के प्रकाश, कार्बन डाइऑक्साइड (CO2) और पानी (H2O) का उपयोग करके ग्लूकोज (भोजन) बनाते हैं और वातावरण में ऑक्सीजन (O2) गैस छोड़ते हैं: 6CO2 + 6H2O + Light -> C6H12O6 + 6O2।"),
        ("hindi-science-gravity", "गुरुत्वाकर्षण और सार्वभौमिक नियम (Gravity / Gurutwakarshan)", "general_science", "physics",
         "गुरुत्वाकर्षण (Gravity / Gravity kya hai) एक मौलिक प्राकृतिक बल है जिसके द्वारा द्रव्यमान या ऊर्जा वाली सभी वस्तुएं एक-दूसरे की ओर आकर्षित होती हैं। सर आइजैक न्यूटन के सार्वभौमिक गुरुत्वाकर्षण नियम के अनुसार, दो पिंडों के बीच आकर्षण बल उनके द्रव्यमान के गुणनफल के समानुपाती और उनके बीच की दूरी के वर्ग के व्युत्क्रमानुपाती होता है (F = G*m1*m2/r^2)। अल्बर्ट आइंस्टीन के सामान्य सापेक्षता सिद्धांत के अनुसार गुरुत्वाकर्षण स्पेस-टाइम (दिक-काल) के वक्रता का परिणाम है।"),
        ("hindi-science-solar-system", "सौर मंडल और ग्रह (The Solar System / Saur Mandal)", "general_science", "astronomy",
         "सौर मंडल (Solar System) सूर्य और उसके चारों ओर गुरुत्वाकर्षण से बंधे खगोलीय पिंडों से मिलकर बना है। सूर्य से दूरी के क्रम में आठ मुख्य ग्रह हैं: बुध (Mercury), शुक्र (Venus), पृथ्वी (Earth), मंगल (Mars), बृहस्पति (Jupiter), शनि (Saturn), यूरेनस (Uranus) और नेपच्यून (Neptune)। आंतरिक ग्रह चट्टानी हैं जबकि बाहरी ग्रह गैस और बर्फ के विशालकाय पिंड हैं।"),
        ("hindi-science-dna", "डीएनए और आनुवंशिकी (DNA and Genetics / DNA kya hai)", "general_science", "biology",
         "डीऑक्सीराइबोन्यूक्लिक एसिड (DNA) जीवों की कोशिकाओं में आनुवंशिक जानकारी ले जाने वाला दोहरा हेलिक्स (Double Helix) अणु है। डीएनए चार न्यूक्लियोटाइड क्षारों (एडेनिन, थाइमिन, साइटोसिन, गुआनिन) से बना होता है और जीवन के विकास, वृद्धि और प्रजनन के सभी जैविक निर्देशों को संग्रहीत करता है।"),

        # --- 2. COMPUTER SCIENCE IN HINDI & HINGLISH ---
        ("hindi-tech-python", "पायथन प्रोग्रामिंग भाषा (Python Programming / Python kya hai)", "computer_science", "programming",
         "पायथन (Python / Python kya hai) एक उच्च-स्तरीय, इंटरप्रिटेड और डायनामिक रूप से टाइप की गई प्रोग्रामिंग भाषा है जिसे गुइडो वैन रोसुम ने बनाया था। अपनी सरल सिंटैक्स और उच्च पठनीयता के कारण, पायथन का व्यापक रूप से डेटा साइंस, मशीन लर्निंग, आर्टिफिशियल इंटेलिजेंस, वेब डेवलपमेंट (FastAPI, Django), और ऑटोमेशन स्क्रिप्टिंग में उपयोग किया जाता है।"),
        ("hindi-tech-dsa", "डेटा संरचनाएं और एल्गोरिदम (Data Structures and Algorithms / DSA kya hai)", "computer_science", "data_structures",
         "डेटा संरचनाएं (Data Structures) कंप्यूटर मेमोरी में डेटा को कुशलतापूर्वक संग्रहीत और व्यवस्थित करने के तरीके हैं (जैसे Array, Linked List, Stack, Queue, Hash Table, Binary Tree, Graph)। एल्गोरिदम (Algorithms) किसी समस्या को हल करने के चरण-दर-चरण निर्देश हैं। एल्गोरिदम की कार्यक्षमता को बिग-ओ (Big-O) नोटेशन द्वारा मापा जाता है।"),
        ("hindi-tech-db", "डेटाबेस, एसक्यूएल और एसिड गुण (Databases and SQL / Database kya hai)", "computer_science", "databases",
         "डेटाबेस प्रबंधन प्रणाली (DBMS / Database kya hai) डेटा को व्यवस्थित और सुरक्षित रूप से संग्रहीत करने का सॉफ्टवेयर है। रिलेशनल डेटाबेस डेटा को पंक्तियों और स्तंभों वाली तालिकाओं (Tables) में रखते हैं, जिन्हें Structured Query Language (SQL) द्वारा क्वेरी किया जाता है। डेटाबेस लेनदेन में ACID नियमों (Atomicity, Consistency, Isolation, Durability) का पालन किया जाता है।"),
        ("hindi-tech-os", "ऑपरेटिंग सिस्टम और मेमोरी प्रबंधन (Operating Systems / OS kya hai)", "computer_science", "operating_systems",
         "ऑपरेटिंग सिस्टम (OS / Operating System kya hai) कंप्यूटर हार्डवेयर और उपयोगकर्ता अनुप्रयोगों के बीच मध्यस्थ सॉफ्टवेयर है (जैसे Linux, Windows, macOS)। यह CPU शेड्यूलिंग, प्रोसेस मैनेजमेंट, वर्चुअल मेमोरी, पेजिंग, डेडलॉक रोकथाम और फाइल सिस्टम का प्रबंधन करता है।"),
        ("hindi-tech-networking", "कंप्यूटर नेटवर्क और इंटरनेट प्रोटोकॉल (Computer Networks / Networking)", "computer_science", "networking",
         "कंप्यूटर नेटवर्क (Computer Networks) परस्पर जुड़े कंप्यूटरों का समूह है जो डेटा साझा करते हैं। OSI मॉडल में 7 परतें होती हैं। इंटरनेट TCP/IP प्रोटोकॉल सूट पर काम करता है। TCP विश्वसनीय और क्रमित डेटा डिलीवरी सुनिश्चित करता है, जबकि UDP कम लेटेंसी वाला तेज कनेक्शन रहित प्रोटोकॉल है। HTTP/HTTPS वेब संचार के लिए उपयोग किया जाता है।"),

        # --- 3. AI & MACHINE LEARNING IN HINDI & HINGLISH ---
        ("hindi-tech-ai", "कृत्रिम बुद्धिमत्ता (Artificial Intelligence - AI / AI kya hai)", "ai_ml", "ai_foundations",
         "कृत्रिम बुद्धिमत्ता (Artificial Intelligence - AI / AI kya hai) कंप्यूटर विज्ञान की वह शाखा है जो ऐसी बुद्धिमान प्रणालियाँ और एल्गोरिदम विकसित करती है जो मानव बुद्धि की आवश्यकता वाले कार्य कर सकें। इसमें कंप्यूटर विज़न (Computer Vision), वाक् पहचान (Speech Recognition / STT), प्राकृतिक भाषा प्रसंस्करण (NLP), तर्क और निर्णय लेने की क्षमता शामिल है।"),
        ("hindi-tech-ml", "मशीन लर्निंग और लर्निंग प्रकार (Machine Learning / ML kya hai)", "ai_ml", "machine_learning",
         "मशीन लर्निंग (Machine Learning / ML kya hoti hai) कृत्रिम बुद्धिमत्ता का एक उपक्षेत्र है जिसमें एल्गोरिदम बिना स्पष्ट रूप से प्रोग्राम किए डेटा और अनुभवों से सीखते हैं। इसके तीन मुख्य प्रकार हैं: सुपरवाइज्ड लर्निंग (लेबल किए गए डेटा से सीखना), अनसुपरवाइज्ड लर्निंग (पैटर्न और क्लस्टर खोजना), और रीइन्फोर्समेंट लर्निंग (रिवॉर्ड और फीडबैक द्वारा निर्णय नीति सीखना)।"),
        ("hindi-tech-transformers-rag", "ट्रांसफॉर्मर, अटेंशन और RAG आर्किटेक्चर (Transformers and RAG / RAG kya hai)", "ai_ml", "rag",
         "ट्रांसफॉर्मर (Transformers) आधुनिक डीप लर्निंग आर्किटेक्चर है जो सेल्फ-अटेंशन (Self-Attention) मैकेनिज्म का उपयोग करता है। रिट्रीवल-ऑगमेंटेड जेनरेशन (RAG / RAG kya hai) एक आधुनिक एआई आर्किटेक्चर है जो लार्ज लैंग्वेज मॉडल (LLM) को बाहरी ज्ञानकोष (FAISS/BM25) से प्रासंगिक दस्तावेज खोजकर सटीक और साक्ष्य-आधारित उत्तर देने में सक्षम बनाता है, जिससे मतिभ्रम (Hallucination) पूरी तरह रुकता है।"),
        ("hindi-tech-faiss", "FAISS वेक्टर सर्च और एम्बेडिंग (FAISS Library / FAISS kya hai)", "ai_ml", "information_retrieval",
         "FAISS (Facebook AI Similarity Search / FAISS kaise kaam karta hai) मेटा एआई द्वारा विकसित एक ओपन-सोर्स सी++ लाइब्रेरी है जो उच्च-आयामी सघन वैक्टर (Dense Vectors) के कुशल समानता खोज और क्लस्टरिंग के लिए अनुकूलित है। यह अरबों वैक्टरों में सटीक कोसाइन सिमिलैरिटी और सन्निकट (ANN / HNSW) खोज का समर्थन करती है।"),

        # --- 4. NOVARON SYSTEM IN HINDI ---
        ("hindi-novaron-sys", "नोवारॉन सिस्टम परिचय और कार्यप्रणाली (NOVARON System Overview)", "novaron_system", "architecture",
         "नोवारॉन (NOVARON / NOVARON kya hai) एक वॉयस-सक्षम, साक्ष्य-आधारित RAG सहायक है जो हिंदी और अंग्रेजी दोनों भाषाओं में बिना किसी गलत जानकारी (Hallucination) के सटीक उत्तर प्रदान करता है। यह FAISS और BM25 का उपयोग करके केवल सत्यापित ज्ञानकोष स्रोतों से उत्तर देता है और अपर्याप्त जानकारी होने पर सुरक्षित इनकार करता है।")
    ]
    docs = []
    for doc_id, title, domain, topic, text in data:
        docs.append({
            "document_id": doc_id,
            "passage_id": f"{doc_id}-1",
            "title": title,
            "domain": domain,
            "topic": topic,
            "language": "hi",
            "source_type": "curated",
            "keywords": [k.lower() for k in title.split()],
            "text": text
        })
    return docs
