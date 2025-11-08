# **Automatisierte Erstellung hybrider OSCAL-Komponentendefinitionen mittels eingeschränkter 1:1 KI-Abbildung**

Dieses Dokument beschreibt ein überarbeitetes Konzeptrahmenwerk für die automatisierte Erstellung von OSCAL 1.1.3 Komponentendefinitionen, welches die Migration von BSI IT-Grundschutz Edition 2023 (Ed2023) zum modernisierten Grundschutz++ (G++) erleichtern soll1. Die Überarbeitung spezifiziert eine Automatisierungsstrategie, die für die Ausführung auf der Google Cloud Platform (GCP) konzipiert ist und Künstliche Intelligenz (KI) für die semantische Abbildung unter einer strikt durchgesetzten Eins-zu-Eins (1:1) Entsprechung zwischen Altanforderungen und modernen Kontrollen nutzt2.

## **1.0.0 Einleitung und strategischer Kontext**

Die Entwicklung vom modulbasierten IT-Grundschutz Edition 2023 hin zur datenzentrierten, vererbungsgesteuerten Grundschutz++ Methodik stellt einen bedeutenden Wandel dar3. Organisationen benötigen Mechanismen zur Migration bestehender Informationssicherheits-Managementsysteme (ISMS), wobei die Nachvollziehbarkeit zu etablierten Implementierungen gewahrt bleiben muss4.

Dieses Rahmenwerk skizziert einen automatisierten Ansatz zur Erstellung von „Transitional Component Definitions“ (Übergangs-Komponentendefinitionen)5. Das Ziel ist es, einen technischen Ed2023 **„Baustein“** auf das am nächsten entsprechende G++ **„Zielobjekt“** abzubilden und anschließend jede einzelne Ed2023 **„Anforderung“** auf genau eine G++ Kontrolle abzubilden6. Dieser Ansatz operiert unter der strikten Einschränkung: **N:M (Viele-zu-Viele) Beziehungen sind untersagt**7.

Diese Vereinfachung priorisiert die Automatisierungsgeschwindigkeit und die erschöpfende Abdeckung von Altanforderungen gegenüber der absoluten semantischen Präzision8. Das Rahmenwerk akzeptiert die inhärenten semantischen Annäherungen, die durch die fundamentalen strukturellen Unterschiede zwischen den beiden Standards notwendig werden9.

## **2.0.0 Methodik und Einschränkungen**

Die Methodik ist durch starre, zur Vereinfachung der Automatisierung entwickelte Einschränkungen definiert, die die semantische Genauigkeit der resultierenden Artefakte erheblich beeinflussen10.

### **2.1.0 Die 1:1 Abbildungseinschränkung**

Das Rahmenwerk schreibt eine strikte 1:1 Abbildung an zwei kritischen Stellen vor11:

* **Baustein zu Zielobjekt:** Jeder technische Ed2023 Baustein (aus den Gruppen SYS, APP, INF, NET, IND) wird auf genau ein G++ Zielobjekt abgebildet12.

* **Anforderung zu Kontrolle:** Jede Ed2023 Anforderung innerhalb eines Bausteins wird auf genau eine G++ Kontrolle abgebildet13.

Diese Einschränkung erzwingt eine Vereinfachung14. Wo eine einzelne Altanforderung in mehrere G++ Kontrollen zerlegt wird, muss die Automatisierung nur die **„beste Übereinstimmung“** auswählen, was zu semantischem Verlust führt15. Umgekehrt, wo mehrere Altanforderungen in einer G++ Kontrolle konsolidiert werden, wird die Abbildung die G++ Kontrollreferenz für jede Altanforderung künstlich replizieren16.

### **2.2.0 Logik zur Abbildungspriorisierung**

Die Auswahl der entsprechenden G++ Kontrolle folgt einer definierten Optimierungslogik17:

* **Semantische Nähe:** Das primäre Kriterium ist die Identifizierung der „engsten Übereinstimmung“ basierend auf einer KI-gesteuerten semantischen Analyse der Anforderungstexte18.

* **Vererbung als Präferenz:** Der G++ Mechanismus der **„Vererbung“** definiert eine Basislinie von Kontrollen für ein gegebenes Zielobjekt19. Falls mehrere G++ Kontrollen eine vergleichbare semantische Nähe aufweisen, wird die Kontrolle priorisiert, die bereits in der vererbten Basislinie des Zielobjekts vorhanden ist20.

* **Globaler Geltungsbereich:** Die Abbildung ist nicht auf die vererbte Basislinie beschränkt21. Wenn die engste semantische Übereinstimmung in einer anderen G++ Praktik außerhalb der vererbten Menge existiert, wird diese ausgewählt, um das Kriterium der „engsten Übereinstimmung“ zu erfüllen22.

### **2.3.0 Metadaten-Verarbeitung**

Die Nachvollziehbarkeit zu Ed2023 wird mittels OSCAL-Eigenschaften (*props*) implementiert23. Gemäß den überarbeiteten Einschränkungen werden diese Metadaten als Freitext ohne definierenden Namensraum (*ns* Attribut weggelassen) aufgenommen24. Dies opfert die standardisierte Interoperabilität, da den Metadaten die formale kontextuelle Definition fehlt, wodurch Alt-Identifikatoren eher als beliebiger Text denn als strukturierte Referenzen behandelt werden25.

## **3.0.0 Automatisierungs-Framework (GCP Cloud Run)**

Die Implementierung nutzt einen GCP Cloud Run Job26. Um die Verwendung von KI (die von Natur aus probabilistisch ist) mit der Anforderung an eine deterministische Verarbeitung während der Generierung in Einklang zu bringen, wird der Workflow in zwei unterschiedliche Phasen unterteilt: Phase 0 (Vorverarbeitung/Kuratierung) und Phase 1 (Generierung/Ausführung)27.

### **3.1.0 Phase 0: Vorverarbeitung – KI-gestützte Crosswalk-Kuratierung**

Die Automatisierungspipeline benötigt eine statische, validierte **„Crosswalk“** – die definitive 1:1 Abbildungstabelle – als Eingabe, um eine deterministische Ausführung zu gewährleisten28. Die KI-Modelle arbeiten in dieser Phase, um die anfänglichen Abbildungen zu generieren, welche anschließend kuratiert werden29.

* **KI-gesteuerte Baustein-Abbildung:** Ein KI-Modell analysiert die technischen Bausteine (SYS, APP, INF, NET, IND) aus Ed202330. Es vergleicht die Beschreibung und den Geltungsbereich des Bausteins (z.B. SYS.1.1 Allgemeiner Server) mit den Definitionen der G++ Zielobjekte, um die beste 1:1 Übereinstimmung zu bestimmen (z.B. Server)31.

* **KI-gesteuerte Kontroll-Abbildung:** Für jede Anforderung wird das KI-Modell aufgerufen, um die einzig beste passende G++ Kontrolle zu finden, wobei die Priorisierungslogik (Abschnitt 2.2.0) eingehalten wird32.

* **Identifizierung verwandter Referenzen (G.2.a):** Gleichzeitig identifiziert die KI weitere verwandte G++ Kontrollen oder Konzepte, die für den Geltungsbereich des Bausteins relevant sind33. Diese werden zur späteren Aufnahme aufgezeichnet34.

* **Experten-Kuratierung und Validierung:** Fachexperten müssen diese KI-vorgeschlagenen Abbildungen validieren, anpassen und **einfrieren**35. Dieser kuratierte Crosswalk wird zum maßgeblichen, statischen Artefakt, das von der operativen Pipeline verwendet wird36. Dieser Schritt ist entscheidend, um sicherzustellen, dass der Cloud Run Job deterministisch ausgeführt wird37.

### **3.2.0 Phase 1: Deterministische Generierungspipeline (Cloud Run Job)**

Der GCP Cloud Run Job führt die folgenden deterministischen Schritte aus und konsumiert dabei den validierten Crosswalk, das G++ Kompendium, G++ Zielobjekt Definitionen und die Ed2023 JSON-Quelldaten (z.B. BSI\_GS\_OSCAL\_current\_2023\_benutzerdefinierte.json)38.

* **Schritt 1: Iteration der technischen Bausteine (G.1 – Deterministisch)** Der Job iteriert deterministisch durch alle relevanten technischen Bausteine (SYS, APP, INF, NET, IND), wie sie im Geltungsbereich des Crosswalks definiert sind39.

* **Schritt 2: Zielobjekt-Identifikation (G.2 – Deterministisch)** Für den aktuellen Baustein wird das entsprechende G++ Zielobjekt direkt aus dem kuratierten Crosswalk abgerufen40.

  * **Schritt 2.a (Verwandte Referenzen):** Der Job ruft die vorab identifizierten verwandten Kontrollen aus den Crosswalk-Daten ab, um sie als OSCAL-Referenzen aufzunehmen (z.B. unter Verwendung von *link*\-Elementen mit *rel="related"*)41.

* **Schritt 3: G++ Kontroll-Vererbungs-Auflösung (G.3 – Deterministisch)** Die Pipeline löst die G++ Kontroll-Basislinie für das identifizierte Zielobjekt auf42. Dies beinhaltet das Durchlaufen der Zielobjekt-Hierarchie unter Verwendung von G++ Metadaten (z.B. UUIDs und *ChildOfUUID* Referenzen) und die Aggregation aller vererbten Kontrollen aus dem G++ Kompendium43. (Obwohl die 1:1 Abbildung im Crosswalk vordefiniert ist, überprüft dieser Schritt den Kontext, der während der Priorisierung in Phase 0 verwendet wurde) 44.

* **Schritt 4: Anforderungs-Verarbeitung und Kontroll-Abbildung (G.4 – Deterministisch)** Der Job iteriert deterministisch durch jede Anforderung, die dem aktuellen Baustein zugeordnet ist45. Die entsprechende 1:1 G++ Kontroll-ID wird direkt aus dem kuratierten Crosswalk abgerufen46.

* **Schritt 5: OSCAL Synthese und Datenanreicherung (G.5 – Deterministisch)** Ein OSCAL *implemented-requirement* Eintrag wird synthetisiert47. Die *control-id* wird auf den G++ Identifikator gesetzt48. Die Pipeline reichert diesen Eintrag dann mit Daten an, die aus der Ed2023 JSON-Quelle extrahiert wurden49. Dies umfasst die Alt-ID, den Titel und andere relevante Attribute (z.B. Implementierungsleitfaden), die als Metadaten-Eigenschaften ohne Namensraum eingebettet werden50.

* **Schritt 6: Serialisierung und Ausgabe (G.6 – Deterministisch)** Die vollständige OSCAL Komponentendefinition wird zusammengebaut51. Das Artefakt wird in JSON serialisiert und unter der Konvention $Zielobjekt-$Baustein.json gespeichert (z.B. Server-SYS.1.1.json)52.

## **4.0.0 OSCAL Implementierung und Struktur**

Die resultierenden Artefakte entsprechen dem OSCAL 1.1.3 Schema53. Die Integration von Altdaten hält sich an die Einschränkung, Namensräume wegzulassen54.

### **4.1.0 Struktur der Komponentendefinition**

Die *component-definition* enthält die Metadaten und die *components*, welche die migrierten Entitäten darstellen55.

***JSON Beispiel (Auszug)***:

JSON

"component-definition" : {  
  "uuid" :  "\[Generierte UUID\]" ,  
  "metadata" : { ... },  
  "components" : \[  
    {  
      "uuid" :  "\[Component UUID\]" ,  
      "type" :  "software" ,  // Oder passender Typ für das Zielobjekt  
      "title" :  "Transitional Component: Server (Abgebildet von SYS.1.1)" ,  
      "description" :  "Eine OSCAL-Komponente, die ein Server Zielobjekt darstellt, mit Kontrollen, die 1:1 vom Ed2023 Baustein SYS.1.1 abgebildet wurden."  
      \[cite: 68\],       "links" : \[  
        // Beispiel für verwandte Referenzen, identifiziert in Schritt 2.a  
        {  
          "href" :  "\#\[UUID\_of\_Related\_G++\_Control\]" ,  
          "rel" :  "related" ,  
          "text" :  "Potenzielle Relevanz für G++ Kontrolle bezüglich spezialisierter Hardware-Sicherheit."  
        }  
      \],  
      "control-implementations" : \[ ... \]  
    }  
  \]  
}

### **4.2.0 Struktur der implementierten Anforderung**

Das *implemented-requirement* Objekt demonstriert die Integration der G++ Autorität und der Ed2023 Metadaten56.

***JSON Beispiel (Auszug)***:

JSON

"implemented-requirements" : \[  
  {  
    "uuid" :  "\[Generierte UUID\]" ,  
    "control-id" :  "ARCH.2.1" ,  // Autoritative G++ Kennung (z.B. Netzsegmente)  
    "props" : \[  
      {  
        "name" :  "ed2023\_legacy\_id" ,  
        // "ns" Attribut absichtlich weggelassen gemäß Einschränkung F  
        "value" :  "NET.1.1.A5"  
      },  
      {  
        "name" :  "ed2023\_legacy\_title" ,  
        "value" :  "Aufteilung des Netzes in Segmente"  
        \[cite: 75\]  
      },  
      {  
        "name" :  "ed2023\_legacy\_guidance" ,  
        // Angereicherte Daten aus der Ed2023 JSON-Quelle (Schritt 5\)  
        "value" :  "\[Extracted implementation guidance text\]"  
      }  
    \],  
    "remarks" :  "Diese G++ Kontrolle ist der designierte 1:1 Nachfolger von NET.1.1.A5 basierend auf dem kuratierten Crosswalk."  
  }  
\]

## **5.0.0 Kritische Analyse und methodische Einschränkungen**

Die dem Rahmenwerk auferlegten Einschränkungen bergen signifikante methodische Risiken, die von jeder Organisation, die diesen Ansatz übernimmt, formal anerkannt werden müssen57.

### **5.1.0 Inhärente semantische Verluste (Die 1:1 Einschränkung)**

Das Verbot von N:M Beziehungen ist die schwerwiegendste Einschränkung58. Angesichts der unterschiedlichen Granularität und Struktur von Ed2023 und G++ gewährleistet diese Einschränkung semantische Ungenauigkeit und Informationsverlust59.

* **Verlust durch Zerlegung (*Decomposition Loss*):** Wenn eine einzelne Ed2023 Anforderung mehrere Sicherheitsaspekte abdeckt, die in mehrere separate G++ Kontrollen zerlegt werden, erzwingt die 1:1 Abbildung die Auswahl von nur einer G++ Kontrolle60. Die verbleibenden Aspekte werden effektiv aus der Abbildung weggelassen, was zu einer unvollständigen Darstellung des ursprünglichen Anforderungsumfangs führt61.

* **Verzerrung durch Konsolidierung (*Consolidation Distortion*):** Wenn mehrere Ed2023 Anforderungen in einer einzigen G++ Kontrolle konsolidiert werden, erfordert die 1:1 Abbildung, dass die G++ Kontrolle für jede Altanforderung wiederholt wird, was potenziell die modernisierte Struktur von G++ verschleiert62.

Die generierten Komponentendefinitionen sind Annäherungen und sollten ohne eine umfassende Expertenüberprüfung nicht als maßgebend für die Compliance-Validierung betrachtet werden63.

### **5.2.0 Kuratierungs-Aufwand und KI-Abhängigkeit**

Obwohl die operative Pipeline (Phase 1\) deterministisch ist, ist sie vollständig von der Qualität des kuratierten Crosswalks (Phase 0\) abhängig64. Die Subjektivität bei der Bestimmung der „einzig besten Übereinstimmung“ macht einen erheblichen Expertenbeitrag während der Kuratierungsphase erforderlich65. Das Risiko, KI-Ungenauigkeiten oder \-Verzerrungen in das ISMS zu propagieren, ist beträchtlich, wenn die Validierung unzureichend ist66. Die anfängliche Investition in die Erstellung eines zuverlässigen Crosswalks ist hoch und erfordert eine laufende Wartung, wenn sich G++ weiterentwickelt67.

### **5.3.0 Interoperabilitätsrisiken (Metadaten ohne Namensraum)**

Die Entscheidung, formale Namensräume für Alt-Metadaten wegzulassen, reduziert die Robustheit und Interoperabilität der OSCAL-Artefakte signifikant68. Ohne Namensräume können automatisierte Tools, die diese Daten konsumieren, den Ursprung oder die Semantik der Alt-Eigenschaften nicht eindeutig bestimmen, was die automatisierte Berichterstellung und Integration innerhalb eines standardisierten OSCAL-Ökosystems erschwert69.

## **6.0.0 Kritische Annahmen**

* **Kuratierbarkeit:** Es wird angenommen, dass Fachexperten die KI-generierten 1:1 Abbildungen trotz der semantischen Fehlausrichtung zwischen den Standards erfolgreich zu einem validierten, statischen Crosswalk kuratieren können70.

* **Datenquellen-Integrität:** Es wird angenommen, dass das G++ Kompendium, die Zielobjekt-Definitionen und das spezifische Ed2023 JSON-Repository zugänglich, strukturell stabil und vollständig sind71.

* **Übergangs-Nutzen:** Es ist verstanden, dass die generierten Artefakte Übergangshilfen darstellen und keine definitive, langfristige Implementierungsstrategie repräsentieren72.  
