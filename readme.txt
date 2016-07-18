Tim 1:
	Rade Radišić  -  E2 42/2015
	Daniel Kupčo  -  R1 8/2015
	Dragoljub Ilić  -  R1 4/2015

Funkcionalnosti:
	- Registracija i logovanje korisnika
	- Korisnik može da edituje svoj profil
	- Prikaz svih repozitorijuma i issue-a (open source)
	- Pretraga i filtriranje repozitorijuma i issue-a
	- CRUD operacije za issue-e, repozitorijume i tagove
	- Dodavanje drugih korisnika kao contributor-a na repozitorijum
	- Dve role: Owner i contributor. Samo owner ima pravo da edituje i
	   i brise svoj repozitorijum, i da dodaje contributor-e. Contributor moze da kreira issue-e i da ih zatvara.
	- Dodavanje komentara i linkovanje commit-a na issue.

SCM proces:
	- Aplikacija se distribuira u vidu Docker kontejnera
	- Baza podataka koju koristi aplikacija nalazi se u posebnom kontejneru
		- Prednost nezavisne izmene verzije aplikacije
	- Prilikom build-a Docker image-a sa Github repozitorijuma uzima se poslednja stabilna verzija (master grana)
	- Razvoj novih feature-a i ispravke bagova za sledeću verziju odvijaju se pretežno na develop grani
		- Po potrebi, pravi se nova lokalna feature grana ukoliko je u pitanju obimniji rad
	- Prilikom release verzije, stabilna develop grana merge-uje se sa postojećom master granom
	
Dragoljub Ilić:
	- Ispravka modela
	- Celokupan dizajn sajta
	- Registracija i autentikacija korisnika
	- Izmena korisničkog profila and lozinke
	- Listing repozitorijuma i issue-a
	- Pretraga, filtriranje i paginacija za repozitorijume i issue-e

Daniel Kupčo:
    - Ispravka modela
    - Generički template-i
    - Primeri generičkih formi (sa validacijom), redirekcije
    - CRUD operacije za repozitorijume, issue-e i komentare
    - Manipulacija contributor-a (typeahead, add, remove)
    - Izmena profilne slike (preko URL-a i image upload)

Rade Radišić:
    - Definicija Django model klasa
    - Izmena konfiguracije baze podataka koju koristi aplikacija (MySQL)
    - CRUD operacije za tag entitet
    - Pisanje Dockerfile-a
    - deploy na server (issuebox-live i issuebox-db kontejneri)
    
