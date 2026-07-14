Sortiranje fotografija po datumu
Python skripta koja prolazi kroz folder (i sve njegove podfoldere, bez obzira na dubinu), pronalazi sve slike i video zapise, sortira ih hronološki po pravom datumu snimanja, i prepoznaje duplikate na osnovu sadržaja fajla.
Šta radi:
	•	Rekurzivno prolazi kroz zadati folder i sve podfoldere
	•	Za svaki fajl očitava datum snimanja iz EXIF/metapodataka (preko exiftool), sa fallback-om na datum fajla na disku ako metapodaci ne postoje
	•	Prepoznaje duplikate poredeći SHA256 hash sadržaja fajla (hvata duplikate čak i kad imaju različita imena)
	•	Kopira sve jedinstvene fajlove u novi izlazni folder, preimenovane sa datumom na početku imena (npr. 2024-03-15_14-30-00_IMG1234.jpg), tako da su hronološki sortirani po imenu
	•	Duplikate NE briše automatski — pravi log fajl (duplikati_log.txt) za pregled pre bilo kakvog brisanja

Zahtevi:
	•	Python 3
	•	exiftool — instalacija preko Homebrew-a: brew install exiftool

Upotreba:
	1	Otvori sortiraj_fotografije.py i podesi promenljive na vrhu fajla: SOURCE_FOLDER = "/putanja/do/foldera/sa/fotografijama"OUTPUT_FOLDER = "/putanja/do/izlaznog/foldera"DELETE_DUPLICATES_FROM_SOURCE = False
	1	Pokreni: python3 sortiraj_fotografije.py
	2	Pregledaj rezultat u OUTPUT_FOLDER i listu duplikata u duplikati_log.txt
	3	Ako se slažeš sa listom duplikata, promeni DELETE_DUPLICATES_FROM_SOURCE = True i pokreni skriptu ponovo — tek tada briše duplikate iz originalnog foldera
Napomena
Skripta kopira fajlove (ne premešta), pa privremeno treba dovoljno slobodnog prostora na disku za i original i kopiju.
——————————————
Napomena 2!
Nisam stigla da finalizujem skriptu - work in progress.  Ukoliko odlucite da je pokrenete - cinite to na sopstvenu odgovornost.
Verzija 5.2
