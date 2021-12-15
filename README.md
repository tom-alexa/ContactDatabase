# ContactDatabase

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
        - //11 | ukáže vše ve 20. dni v měsíci
        - 2003// | zkáže vše v roce 2003
        - 2003/1/ | ukáže vše v roce 2003 a zároveň v lednu
        - 2003/1/11 | ukáže vše v roce 2003 a zároveň v lednu a zároveň v 11. dni v měsíci
    - l -g {skupina} | ukáže všechni kontakty ve skupině

- vloží řádek
    - i | vloží kontakt
    - i n | vloží číslo

- upraví řádek
    - u | upraví kontakt
    - u n | upraví číslo

- odstraní řádek
    - u | odstraní kontakt
    - u n | odstraní číslo
