# **Konzept zur Abbildung von Zielobjekt-Bausteinen im Grundschutz++ mittels OSCAL**

**Datum:** 22\. Oktober 2025

## **1\. Einleitung und Zielsetzung**

Die Modernisierung zum Grundschutz++ (GS++) ersetzt die Struktur der bisherigen IT-Grundschutz-Bausteine durch ein datenzentriertes Modell, das auf Praktiken und Zielobjekt-Typen basiert. Zielobjekt-Typen repräsentieren die Bestandteile eines Informationsverbundes (Assets) und sind hierarchisch organisiert. Diese Hierarchie ermöglicht die Vererbung von Anforderungen von allgemeinen Typen (z.B. "Server") zu spezifischen Ausprägungen (z.B. "Windows Server" oder "Linux Server") und muss auch für singuläre Typen (z.B. "Router", "Gebäude") funktionieren.  
Dieses Dokument definiert das Konzept der "Zielobjekt-Bausteine". Diese dienen als digitale, maschinenlesbare Vorlagen, die die Funktionalität der ehemaligen Bausteine ersetzen. Sie unterstützen Anwender bei der Strukturmodellierung, indem sie für jeden Zielobjekt-Typ die relevanten Anforderungen bündeln und standardisierte Umsetzungshinweise bereitstellen. Das Konzept basiert auf dem Open Security Controls Assessment Language (OSCAL) Framework und setzt die GS++ Methodik stringent um.

## **2\. Definition und Abgrenzung**

### **2.1 Definition Zielobjekt-Baustein**

Ein Zielobjekt-Baustein ist ein normatives, primär vom BSI bereitgestelltes Artefakt-Set, das einen spezifischen Zielobjekt-Typ kapselt. Er umfasst drei Kernelemente:

1. **Identität:** Die Definition und Klassifizierung des Zielobjekt-Typs.  
2. **Anforderungsumfang (Das "Was"):** Die exakte Menge der relevanten Anforderungen aus dem GS++ Kompendium für diesen Typ, unter Berücksichtigung der vollständigen Vererbungshierarchie.  
3. **Umsetzungshinweise (Das "Wie"):** Standardisierte Beschreibungen und Maßnahmen, wie diese Anforderungen für den Zielobjekt-Typ idealtypisch umgesetzt werden (Soll-Umsetzung).

### **2.2 Abgrenzung zu Blaupausen**

Die Abgrenzung zu Blaupausen (Blueprints) ist essenziell für das Gesamtmodell:

* **Zielobjekt-Bausteine** sind modulare, komponentenzentrierte Building Blocks. Sie definieren das Standard-Soll für einen *einzelnen Asset-Typ* (z.B. "Windows Server"). Sie sind weitgehend kontextunabhängig.  
* **Blaupausen** sind kontextspezifische Sicherheitsbaselines (umgesetzt als \<OSCAL Profile\>). Sie definieren das Soll für einen *Anwendungsfall* oder einen *Informationsverbund*. Blaupausen nutzen und kombinieren Anforderungen für verschiedene Asset-Typen und Praktiken und führen spezifisches Tailoring (z.B. Parametrisierung, Festlegung des Sicherheitsniveaus) durch.

## **3\. Technisches Modell: Das Zwei-Säulen-Modell**

Die Realisierung der Zielobjekt-Bausteine in OSCAL erfolgt durch ein Zwei-Säulen-Modell, das auf der Grundlage des GS++ Katalogs aufbaut.

1. **Die Katalog-Basis:** Das GS++ Kompendium als \<OSCAL Catalog\> liefert alle Anforderungen (\<Controls\>).  
2. **Säule 1: Zielobjekt-Profile (Anforderungsumfang):** Für jeden Zielobjekt-Typ wird ein \<OSCAL Profile\> erstellt. Dieses selektiert präzise alle relevanten Anforderungen, ggf. differenziert nach Sicherheitsniveaus.  
3. **Säule 2: Zielobjekt-Component-Definition (Identität und Umsetzung):** Für jeden Zielobjekt-Typ wird eine \<OSCAL Component Definition\> erstellt. Diese definiert die Identität des Typs und enthält standardisierte Umsetzungshinweise.

Das Set aus der Component Definition (Säule 2\) und den zugehörigen Profilen (Säule 1\) bildet den Zielobjekt-Baustein.

## **4\. Umsetzung in OSCAL im Detail**

### **4.1 Säule 1: Zielobjekt-Profile und Vererbung (Das "Was")**

Das Zielobjekt-Profil definiert den Anforderungsumfang. Die korrekte Abbildung der GS++ Vererbungshierarchie ist fundamental und wird durch **Profile Chaining** (kaskadierte Profil-Importe) realisiert.  
**Mechanismus:** Ein spezifisches Profil importiert das Profil seines direkten Eltern-Zielobjekts und erweitert dieses um zusätzliche, spezifische Anforderungen aus dem Katalog.  
**Beispiel:** Hierarchie "IT-System" \-\> "Server" \-\> "Windows Server".

1. **Profil "IT-System":** Importiert den GS++ Katalog und selektiert alle Controls für "IT-System".  
2. **Profil "Server":** Importiert das Profil "IT-System" und fügt die spezifischen Server-Anforderungen aus dem Katalog hinzu.  
3. **Profil "Windows Server":** Importiert das Profil "Server" und fügt die spezifischen Windows-Anforderungen aus dem Katalog hinzu.

\<\!-- end list \--\>  
`# Beispiel: profile-windows-server.yaml (Auszug)`  
`profile:`  
  `metadata:`  
    `title: "Zielobjekt-Profil: Windows Server"`  
  `imports:`  
    `# 1. Vererbung durch Import des Eltern-Profils`  
    `- href: "profile-server.yaml"`  
      `include-all: {}`  
    `# 2. Erweiterung durch Import spezifischer Controls aus dem Catalog`  
    `- href: "gs-plus-catalog.yaml"`  
      `include-controls:`  
        `- with-ids: ["WIN.1.1", "WIN.1.2"]`

Die OSCAL Profile Resolution Engine löst diese Kaskade automatisch auf. Das Ergebnis ist die vollständige Menge aller geerbten und direkten Anforderungen. Dieses Modell funktioniert identisch für singuläre Zielobjekte wie "Router", die ebenfalls von übergeordneten Typen (z.B. "Netzkomponente") erben.

### **4.2 Säule 2: Zielobjekt-Component-Definition (Das "Wie" und Identität)**

Die \<OSCAL Component Definition\> definiert die Identität des Zielobjekt-Typs und stellt Umsetzungshinweise bereit.  
**Struktur:** Sie definiert einen standardisierten Komponenten-Typ (\<component\>) und nutzt den \<control-implementations\> Block, um standardisierte Umsetzungshinweise mittels \<implemented-requirement\> zu hinterlegen.  
**Strategie der Entkopplung:** Um die Wiederverwendbarkeit zu maximieren und Redundanz zu vermeiden (z.B. wenn separate Profile für unterschiedliche Sicherheitsniveaus existieren), wird die Component Definition von spezifischen Profilen entkoppelt.  
**Technische Umsetzung der Entkopplung:** Das source-Attribut innerhalb von \<control-implementations\> wird weggelassen. Die Component Definition listet explizit die control-ids auf, für die sie Umsetzungshinweise bereitstellt.  
`# Beispiel: component-definition-windows-server.yaml (Auszug)`  
`component-definition:`  
  `components:`  
    `- uuid: <uuid-comp-winsrv>`  
      `type: operating-system`  
      `title: "Windows Server"`

  `control-implementations:`  
    `- uuid: <uuid-impl-winsrv>`  
      `# 'source' wird weggelassen, um die Entkopplung von spezifischen Profilen zu ermöglichen`  
      `description: "Standardisierte Umsetzungshinweise für Windows Server."`  
      `implemented-requirements:`  
        `- control-id: "SYS.1.1" # Beispiel: Systemhärtung`  
          `description: "Die Härtung sollte zentral über Group Policy Objects (GPO) gemäß BSI-Empfehlung XYZ erfolgen."`

Diese Entkopplung stellt sicher, dass nur eine Component Definition pro Zielobjekt-Typ gepflegt werden muss, unabhängig von den verschiedenen Profilen (Sicherheitsniveaus), die sie nutzen.

## **5\. Integration in den GS++ Prozess (Strukturmodellierung und SSP)**

Die Zielobjekt-Bausteine werden in der Phase der Strukturmodellierung und bei der Erstellung des Sicherheitskonzepts (System Security Plan, SSP) genutzt. Die Architektur ermöglicht eine effiziente SSP-Erstellung durch "Pre-filling".

### **5.1 Asset-Modellierung und Mapping**

Die Institution erfasst ihre Assets (z.B. "Server DC01") und ordnet sie dem spezifischsten passenden Zielobjekt-Typ zu (z.B. "Windows Server").

### **5.2 Anforderungsmodellierung und SSP-Erstellung (Pre-filling)**

Der Prozess wird idealerweise durch ein ISMS-Tool unterstützt:

1. **Auswahl des Profils (Säule 1):** Der Anwender wählt das passende Zielobjekt-Profil basierend auf dem Typ und dem angestrebten Sicherheitsniveau (z.B. "Windows Server (Standard)"). Dieses Profil wird im SSP mittels \<import-profile\> referenziert (oder ist bereits Teil einer übergeordneten Blaupause).  
2. **Instanziierung der Komponente:** Das Asset "DC01" wird als \<OSCAL Component\> im SSP instanziiert.  
3. **Nutzung der Component Definition (Pre-filling, Säule 2):** Das Tool identifiziert die zugehörige Component Definition. Es gleicht die Anforderungen aus dem importierten Profil (Schritt 1\) mit den Umsetzungshinweisen in der Component Definition ab.  
4. **Automatischer Import:** Die standardisierten Umsetzungshinweise werden automatisch in den SSP des Anwenders importiert (als \<by-component\> Einträge für "DC01").  
5. **Kontextspezifische Anpassung:** Der Anwender prüft die importierten Standard-Hinweise und passt sie an die spezifische Realität seines Assets an.

Dieser "Pre-filling"-Ansatz reduziert den Dokumentationsaufwand erheblich.

## **6\. Fazit**

Das Zwei-Säulen-Modell bietet eine robuste und methodisch konforme Umsetzung der Zielobjekt-Bausteine im GS++:

* **Methodische Konformität:** Die GS++ Vererbungshierarchie wird durch Profile Chaining (Säule 1\) standardkonform, transparent und wartbar abgebildet.  
* **Effizienz und Wartbarkeit:** Die Entkopplung der Component Definition (Säule 2\) von spezifischen Profilen reduziert Redundanz und Pflegeaufwand beim BSI.  
* **Effizienzsteigerung beim Anwender:** Die Bereitstellung von standardisierten Umsetzungshinweisen in der Component Definition beschleunigt die Erstellung des SSP durch Pre-filling erheblich.  
* **Klare Rollen:** Die Rollen von Zielobjekt-Bausteinen als normative Building Blocks und Blaupausen als kontextspezifisches Tailoring sind technisch sauber getrennt.