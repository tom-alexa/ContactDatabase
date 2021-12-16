# ContactDatabase

## Rozdíly úkolu a githubu

- umístění databáze
    - github: ve složce database
    - úkol: ve stejné složce jako dbapp.py

## Funkce

Aplikace slouží k práci s databází na konktakty
- ukončí aplikaci
    - quit
    - exit
    - q
    - e

- ukáže pomocnou tabulku
    - help
    - h

- ukáže tabulku
    - l | ukáže kontakty
    - l -t {c, n, p, g} | ukáže tabulku pro kontakty, čísla, prefixi a skupiny
    - l -n {číslo} | ukáže podobné kontakty podle čísla
    - l -d {datum} | ukáže kontakty s datem narození v jednom z daných hodnot
        - //11 | ukáže všechny kontakty v 11. dni v měsíci
        - 2003// | ukáže všechny kontakty v roce 2003
        - 2003/1/ | ukáže všechny kontakty v roce 2003 nebo v lednu
        - 2003/1/11 | ukáže všechny kontakty v roce 2003 nebo v lednu nebo v 11. dni v měsíci
    - l -g {skupina} | ukáže všechny kontakty ve skupině

- vloží řádek
    - i | vloží kontakt
    - i n | vloží číslo

- upraví řádek
    - u | upraví kontakt
    - u n | upraví číslo

- odstraní řádek
    - u | odstraní kontakt
    - u n | odstraní číslo
