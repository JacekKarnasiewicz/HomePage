Koncepcja:

1) Potrzebujemy jednego miejsca w którym możemy bezpiecznie przechowywać informacje odnoszące się do naszych kont osobistych i w każdej chwili chcemy mieć do nich dostęp

2) Każda zarejestrowana osoba ma wgląd i może modyfikować tylko i wyłącznie swoje wpisy, nie mam możliwości podglądu wpisów innych użytkowników

3) W razie wycieku danych z serwera, hasła w bazie danych są zaszyfrowane, natomiast podgląd ich z przeglądarki jest niezaszyfrowany(mając wiele kont często zapominamy jakie hasło było do którego konta, tak więc dzięki naszej aplikacji możemy, spokojnie przypomnieć sobie, które hasła były do których kont)

4) Nie narzucamy jakie powinny byc hasła do naszych kont(jest to zadanie poszczególnych portali na których założyliśmy konta), natomiast aplikacja mam wbudowaną funkcjonalność która pomaga nam ocenić jak dobre i bezpieczne jest nasze hasło, co może doprowadzić klienta do zmiany orginalnego hasła - nie chcemy uniemożliwiać wpisów słabych haseł jeśli już takie istnieją i z takich korzystamy, ale zostaniemy poinformowani o 'sile' naszego hasła

5) Gdybyśmy planowali połączyc nasz moduł z innymi zewnętrznymi aplikacjami to mamy dostęp do restowego api, które ułatwi nam takie połączenia

6) Każdy wpis można szybko i wygodnie tworzyć, edytować i usuwać

7) Password entropy - wybrałem troszkę inną drogę walidacji. Postanowiłem nie testować przy każdym wpisie nowego znaku całych list(które mi przekazaliści), wydawało mi się to troche zbyt uciążliwe dla potencjalnego klienta, tym bardziej że listy słów i najczęstszych haseł były bardzo duże. Po przeglądnięciu tych listy doszedłem do wniosku że naprawde dobre hasło którego nie znajdziemy na tych listach powinno mieć przynajmniej 8 znaków, zawierać przynajmniej jedną dużą i małą liter, cyfre i znak specjalny. Przy takim podejściu bardzo szybko sprawdzimy 'siłe' naszego hasła i nie będziemy niepotrzebnie przeczesywać setek tysięcy wpisów z dostarczonych list.
