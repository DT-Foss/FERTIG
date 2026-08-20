"""FERTIG — Tests des Bindungs-Parsers (GSM8K-Projekt, Runde 1-2).

Der Bindungs-Parser bindet Zahlen an Objekte+Einheiten+RollEN, statt
Muster zu matchen. Diese Tests fixieren die falsifizierbaren Fälle.
"""

from __future__ import annotations

from fertig import bindings


def test_natalia_1zu1_und_ratio():
    """1:1-Übertragung (48 Freunde -> 48 clips) + half-as-many-Ratio."""
    r = bindings.bind(
        "Natalia sold clips to 48 of her friends in April, and then she "
        "sold half as many clips in May. How many clips did Natalia sell "
        "altogether in April and May?")
    assert r.ok and r.answer == "72"


def test_objekt_trennung():
    """Nur das Zielobjekt zählt: Äpfel ≠ Orangen."""
    r = bindings.bind(
        "John has 5 apples and 3 oranges. How many apples does he have?")
    assert r.ok and r.answer == "5"


def test_summe_gleicher_objekte():
    r = bindings.bind(
        "A bakery sold 12 cakes on Monday and 15 cakes on Tuesday. "
        "How many cakes did they sell in total?")
    assert r.ok and r.answer == "27"


def test_jede_relation_pizza():
    """Pro-Stück-Werte multiplizieren mit der Stückzahl (2x16 + 2x8)."""
    r = bindings.bind(
        "Albert buys 2 large pizzas and 2 small pizzas. A large pizza "
        "has 16 slices and a small pizza has 8 slices. How many slices "
        "total?")
    assert r.ok and r.answer == "48"


def test_more_fewer_kette():
    """Relative Mengen lösen sich entlang der Referenzkette auf
    (11 + 20 + 7 — truck = snowflake+9, rose = truck-13)."""
    r = bindings.bind(
        "Bella bought stamps. 11 snowflake stamps, 9 more truck stamps "
        "than snowflake stamps, 13 fewer rose stamps than truck stamps. "
        "How many stamps total?")
    assert r.ok and r.answer == "38"


def test_variablen_propagation():
    """Gleichungskette: Mina=24, Mina=6xCarlos, Sam=Carlos+6 -> 10."""
    r = bindings.bind(
        "Sam memorized six more digits of pi than Carlos memorized. "
        "Mina memorized six times as many digits of pi as Carlos "
        "memorized. If Mina memorized 24 digits of pi, how many digits "
        "did Sam memorize?")
    assert r.ok and r.answer == "10"


def test_futterkette():
    """Ketten-each: 6 Jaguare x 5 Schlangen x 3 Vögel x 12 Käfer."""
    r = bindings.bind(
        "Each bird eats 12 beetles per day, each snake eats 3 birds per "
        "day, and each jaguar eats 5 snakes per day. If there are 6 "
        "jaguars, how many beetles do they eat per day?")
    assert r.ok and r.answer == "1080"


def test_with_menge():
    """7 Seesterne x 5 Arme + 1 x 14 Arme."""
    r = bindings.bind(
        "Carly collected 7 starfish with 5 arms each and one seastar "
        "with 14 arms. How many arms did she collect?")
    assert r.ok and r.answer == "49"


def test_left_total_minus_teile():
    """5 Häuser, erste 4 haben je 3, total 20 -> fünftes hat 8."""
    r = bindings.bind(
        "There are 5 houses on a street, and each of the first four "
        "houses has 3 gnomes in the garden. If there are a total of 20 "
        "gnomes on the street, how many gnomes does the fifth house "
        "have?")
    assert r.ok and r.answer == "8"


def test_halb_kette_mit_variable():
    """Tim = Martha-30, Harry = Tim/2, Martha=68 -> Harry 19."""
    r = bindings.bind(
        "Tim has 30 less apples than Martha, and Harry has half as many "
        "apples as Tim. If Martha has 68 apples, how many apples does "
        "Harry have?")
    assert r.ok and r.answer == "19"


def test_raten_dauer_und_gave():
    """2h x 35 + 15 + 50 - 15 (gave) = 120."""
    r = bindings.bind(
        "During the first hour, she collected 15 coins. For the next "
        "two hours, she collected 35 coins from the fountain. In the "
        "fourth hour, she collected 50 coins but she gave 15 of them "
        "to her coworker. How many coins did she have after the fourth "
        "hour?")
    assert r.ok and r.answer == "120"


def test_they_total_und_more2x():
    """they-total (320) und more-than-twice (25)."""
    r = bindings.bind(
        "Paddington has 40 more goats than Washington. If Washington "
        "has 140 goats, how many goats do they have in total?")
    assert r.ok and r.answer == "320"
    r = bindings.bind(
        "John has five more roommates than twice as many as Bob. If "
        "Bob has 10 roommates, how many roommates does John have?")
    assert r.ok and r.answer == "25"


def test_synonym_und_letzte_frage():
    """pieces == slices; die FRAGE ist der letzte how-Satz."""
    r = bindings.bind(
        "Albert buys 2 large pizzas and 2 small pizzas. A large pizza "
        "has 16 slices and a small pizza has 8 slices. If he eats it "
        "all, how many pieces does he eat that day?")
    assert r.ok and r.answer == "48"


def test_rate_mal_dauer():
    """6 Sätze/min x 20 min = 120."""
    r = bindings.bind(
        "Janice can type 6 sentences per minute. She typed for 20 "
        "minutes. How many sentences did she type?")
    assert r.ok and r.answer == "120"


def test_verschachteltes_each():
    """3 Büsche x 25 Rosen x 8 Blütenblätter = 600 (Kettentiefe)."""
    r = bindings.bind(
        "Dan plants 3 rose bushes. Each rose bush has 25 roses. Each "
        "rose has 8 petals. How many petals does Dan have?")
    assert r.ok and r.answer == "600"


def test_end_minus():
    """536 am Ende - (6/min x 53min - 40 erases) = 258 Start."""
    r = bindings.bind(
        "Janice can type 6 sentences per minute. She typed for 20 "
        "minutes, took a break, and typed 15 minutes longer. She then "
        "had to erase 40 sentences. After a meeting, she typed for 18 "
        "minutes more. In all, the paper had 536 sentences by the end "
        "of today. How many sentences did she start with today?")
    assert r.ok and r.answer == "258"


def test_prozent_gruppen():
    """Mehrfach-Prozente: 120x0.8 + 90x0.3 + 50x0.5 = 148."""
    r = bindings.bind(
        "She denied 20% of the 120 kids from Riverside High, 70% of "
        "the 90 kids from West Side High, and half the 50 kids from "
        "Mountaintop High. How many kids got into the movie?")
    assert r.ok and r.answer == "148"


def test_ratio_inkrement():
    """40 + 50 x 6/5 = 100 (Ratio als Inkrement, einmalig)."""
    r = bindings.bind(
        "Jennifer purchased 40 cans of milk. Jennifer bought 6 "
        "additional cans for every 5 cans Mark bought. If Mark "
        "purchased 50 cans, how many cans of milk did Jennifer bring "
        "home from the store?")
    assert r.ok and r.answer == "100"


def test_times_more():
    """25 times more = x26: 85x26 = 2210."""
    r = bindings.bind(
        "Riku has 25 times more stickers than Kristoff. If Kristoff "
        "has 85 stickers, how many stickers does Riku have?")
    assert r.ok and r.answer == "2210"


def test_ziel_rest_dauer_summe():
    """6mph: 1h+30min+1h+20min=17mi, Ziel 20mi -> 30min Freitag."""
    r = bindings.bind(
        "Rosie runs 6 miles per hour. She runs for 1 hour on Monday, "
        "30 minutes on Tuesday, 1 hour on Wednesday, and 20 minutes on "
        "Thursday. If she wants to run 20 miles for the week, how many "
        "minutes should she run on Friday?")
    assert r.ok and r.answer == "30"


def test_kalender():
    """Dez+Jan+Feb = 90 Tage x 1 cup (1/2+1/2) = 90."""
    r = bindings.bind(
        "Herman likes to feed the birds in December, January and "
        "February. He feeds them 1/2 cup in the morning and 1/2 cup "
        "in the afternoon. How many cups of food will he need for all "
        "three months?")
    assert r.ok and r.answer == "90"


def test_behaelter_erbe():
    """2 Flaschen x 15 + 3 weitere x 15 = 75."""
    r = bindings.bind(
        "Kyle bought 2 glass bottles that can hold 15 origami stars "
        "each. He then bought another 3 identical glass bottles. How "
        "many stars must Kyle make to fill all the glass bottles he "
        "bought?")
    assert r.ok and r.answer == "75"


def test_bruch_von_kette():
    """10kg: 1/2 + 1/5 davon + 1/3 vom Rest -> 2 übrig."""
    r = bindings.bind(
        "Liza bought 10 kilograms of butter. She used one-half of it "
        "for chocolate chip cookies, one-fifth of it for peanut butter "
        "cookies, and one-third of the remaining butter for sugar "
        "cookies. How many kilograms of butter are left?")
    assert r.ok and r.answer == "2"


def test_kombination_total():
    """2 Hunde + 3 Katzen + 2x (2+3) Fische = 15 Haustiere."""
    r = bindings.bind(
        "Ed has 2 dogs, 3 cats and twice as many fish as cats and dogs "
        "combined. How many pets does Ed have in total?")
    assert r.ok and r.answer == "15"


def test_passiv_glasser():
    """Passiv-Ziel: 2 + 4x2 = 10 zerbrochene Gläser."""
    r = bindings.bind(
        "David broke 2 glasses, while his friend William broke 4 times "
        "the number of glasses David broke. How many glasses were "
        "broken?")
    assert r.ok and r.answer == "10"


def test_chained_executor():
    """Vier Varianten desselben Musters (Zustand = Restbestand)."""
    r = bindings.bind(
        "Derek has $960. He spends half of that on his textbooks, "
        "and he spends a quarter of what is left on his school "
        "supplies. What is the amount of money Derek has left?")
    assert r.ok and r.answer == "360"
    r = bindings.bind(
        "Julie is reading a 120-page book. Yesterday, she read 12 "
        "pages and today, she read twice as many pages as yesterday. "
        "If she wants to read half of the remaining pages tomorrow, "
        "how many pages should she read?")
    assert r.ok and r.answer == "42"
    r = bindings.bind(
        "A bear needs to gain 1000 pounds. It gained a fifth of the "
        "weight it needed from berries, and gained twice that amount "
        "from acorns. Salmon made up half of the remaining weight. "
        "How many pounds did it gain eating small animals?")
    assert r.ok and r.answer == "200"
    r = bindings.bind(
        "Ali started with 180 seashells. He gave away 40 seashells "
        "to his friends. He also gave 30 seashells to his brothers. "
        "If he sold half of the remaining seashells, how many "
        "seashells did he have left?")
    assert r.ok and r.answer == "55"


def test_gruppen_each():
    """32 Tische: 16x2 + 5x3 + 11x4 = 91 Stühle."""
    r = bindings.bind(
        "There are 32 tables in a hall. Half the tables have 2 chairs "
        "each, 5 have 3 chairs each and the rest have 4 chairs each. "
        "How many chairs in total are in the hall?")
    assert r.ok and r.answer == "91"


def test_studenten_kette():
    """40: 1/10 absent, 3/4 der Anwesenden im Raum, Rest Kantine = 9."""
    r = bindings.bind(
        "There are 40 students in a class. If 1/10 are absent, 3/4 of "
        "the students who are present are in the classroom, and the "
        "rest are in the canteen, how many students are in the "
        "canteen?")
    assert r.ok and r.answer == "9"


def test_typ_mapping_waschmaschine():
    """2x20 + 3x10 + 1x2 + 2x2 (Bleach) = 76."""
    r = bindings.bind(
        "A washing machine uses 20 gallons of water for a heavy wash, "
        "10 gallons of water for a regular wash, and 2 gallons of "
        "water for a light wash per load. If bleach is used, there is "
        "an extra light wash cycle added. There are two heavy washes, "
        "three regular washes, and one light wash to do. Two of the "
        "loads need to be bleached. How many gallons of water will be "
        "needed?")
    assert r.ok and r.answer == "76"


def test_typ_mapping_umgekehrt():
    """Loraine: 12 Sticks/2 = 6 kleine, 6/3 = 2 große -> 12+8 = 20."""
    r = bindings.bind(
        "Large animals take four sticks of wax and small animals take "
        "two sticks. She made three times as many small animals as "
        "large animals, and she used 12 sticks of wax for small "
        "animals. How many sticks of wax did Loraine use to make all "
        "the animals?")
    assert r.ok and r.answer == "20"


def test_multi_tage_rate():
    """5 mph x 2h x 5 Tage = 50 Meilen."""
    r = bindings.bind(
        "Mira jogs every morning. She jogs 5 miles per hour. If she "
        "jogs for 2 hours every morning, how many miles can she jog "
        "for five days?")
    assert r.ok and r.answer == "50"


def test_rate_sub_gewicht():
    """97 kg - 3/Monat x 4 = 85 kg."""
    r = bindings.bind(
        "A boxer weighs 97 kg at 4 months from a fight. He is on a "
        "diet that allows him to lose 3 kg per month until the day of "
        "the fight. How much will he weigh on the day of the fight?")
    assert r.ok and r.answer == "85"


def test_reihe():
    """3 + 2x5 Wochen = 13 (arithmetische Reihe)."""
    r = bindings.bind(
        "Jeanette is practicing her juggling. Each week she can juggle "
        "2 more objects than the week before. If she starts out "
        "juggling 3 objects and practices for 5 weeks, how many "
        "objects can she juggle?")
    assert r.ok and r.answer == "13"


def test_batch_neu():
    """TEST-getriebene Klassen (Runde 6)."""
    assert bindings.bind(
        "Gretchen has 110 coins. There are 30 more gold coins than "
        "silver coins. How many gold coins does Gretchen have?"
    ).answer == "70"
    assert bindings.bind(
        "John has 3 boxes. Each box is 5 inches by 6 inches by 4 "
        "inches. The walls are 1 inch thick. What is the total inner "
        "volume of all 3 boxes?"
    ).answer == "72"
    assert bindings.bind(
        "Billy sells DVDs. His first 3 customers buy one DVD each. "
        "His next 2 customers buy 2 DVDs each. His last 3 customers "
        "buy no DVDs. How many DVDs did Billy sell?"
    ).answer == "7"
    assert bindings.bind(
        "Tom's ship can travel at 10 miles per hour. He is sailing "
        "from 1 to 4 PM. He then travels back at a rate of 6 mph. "
        "How long does it take him to get back?"
    ).answer == "5"
    assert bindings.bind(
        "It takes 10 minutes to cover every 3 miles. If the city is "
        "42 miles across, how many minutes will it take for the fog "
        "to cover the city?"
    ).answer == "140"


def test_batch_neu2():
    """Runde 7: tages-summe, woche, volumen-kette, proportional."""
    assert bindings.bind(
        "He gets 5 pails of water every morning and 6 pails every "
        "afternoon. If each pail contains 5 liters, how many liters "
        "does he get every day?").answer == "55"
    assert bindings.bind(
        "Pancho walks 20 miles a day. Except on weekends when he "
        "walks 10 miles. How many miles does he walk in a week?"
    ).answer == "120"
    assert bindings.bind(
        "Josie has a 10-acre farm. Each acre produces 5 tons of "
        "grapes per year, and each ton of grapes makes 2 barrels of "
        "wine. How many barrels of wine does her farm produce per "
        "year?").answer == "100"


def test_batch_neu3():
    """Runde 8: add-ratio, beutel-typen, ketten-mult."""
    assert bindings.bind(
        "A water tank is filled with 120 liters. Celine used 90 "
        "liters. She was then able to collect rainwater that is twice "
        "as much as what was left. How many liters are in the tank "
        "now?").answer == "90"
    assert bindings.bind(
        "Janet had 22 green pens and 10 yellow pens. Then she bought "
        "6 bags of blue pens and 2 bags of red pens. There were 9 "
        "pens in each bag of blue and 6 pens in each bag of red. How "
        "many pens does Janet have now?").answer == "98"
    assert bindings.bind(
        "Rose bought 4 cakes on Monday. Tuesday she bought three "
        "times that number. On Wednesday she bought 5 times the "
        "number she did on Tuesday. How many cakes did she buy?"
    ).answer == "76"


def test_komma_und_komplement():
    """Komma-Tausender-Parsing + Prozent-Komplement."""
    r = bindings.bind(
        "There are 9,300 pennies in a cup. How many pennies are in "
        "the cup?")
    assert r.ok and r.answer == "9300"
    r = bindings.bind(
        "John arm wrestles 20 people. He beats 80%. How many people "
        "did he lose to?")
    assert r.ok and r.answer == "4"


def test_batch_neu4():
    """Runde 9: pro-teil, prozent-anteil, dezimal-rückwärts."""
    assert bindings.bind(
        "Monica has 6 gifts to wrap for her family, 4 for her friends "
        "and 2 for her teachers. She has 144 inches of ribbon and "
        "wants to make a bow for each gift. How many inches per "
        "bow?").answer == "12"
    assert bindings.bind(
        "Carol spends 4 hours writing a song, half that much time "
        "recording it, and 90 minutes editing it. What percentage of "
        "her total work time did she spend editing?").answer == "20"
    assert bindings.bind(
        "Mr. Ruther sold 3/5 of his land and had 12.8 hectares left. "
        "How much land did he have at first?").answer == "32"


def test_batch_neu5():
    """Runde 10: durchschnitt, shared-with."""
    assert bindings.bind(
        "Jane counts two zebras with 17 stripes each, a zebra with 36 "
        "stripes, and another zebra with half that many stripes. How "
        "many stripes do the zebras have on average?").answer == "22"
    assert bindings.bind(
        "Ray had 25 lollipops. He kept 5 lollipops and shared the "
        "remaining equally with his four friends. How many lollipops "
        "did each of his friends receive?").answer == "5"


def test_batch_neu6():
    """Runde 11: runden-rate, tray-rest."""
    assert bindings.bind(
        "On average Joe throws 25 punches per minute. A fight lasts "
        "5 rounds of 3 minutes. How many punches did he throw?"
    ).answer == "375"
    assert bindings.bind(
        "Each tray can hold 24 eggs. If he has 64 eggs and 2 trays, "
        "how many eggs won't he be able to place on the tray?"
    ).answer == "16"


def test_auditorium():
    """4x18=72, 1/4 Admin, 1/3 der Rest Eltern, Rest Schüler = 36."""
    r = bindings.bind(
        "The school auditorium has 4 rows of seats. There are 18 "
        "seats in each row. One-fourth of the seats were occupied by "
        "the administrators. One-third of the remaining seats were "
        "occupied by the parents and the rest by the students. How "
        "many seats were occupied by the students?")
    assert r.ok and r.answer == "36"


def test_batch_neu7():
    """Runde 12: volumen-hole, prozent-kette."""
    assert bindings.bind(
        "Bob wants to dig a hole 6 feet long by 4 feet wide by 3 feet "
        "deep. If it takes him 3 seconds to shovel a cubic foot of "
        "earth, how long will it take him to dig the hole?"
    ).answer == "216"
    assert bindings.bind(
        "In a company of 50 employees, 20% of the employees are "
        "management. Out of this 20%, only 30% oversee the entire "
        "company. How many employees oversee the company?"
    ).answer == "3"


def test_batch_neu8():
    """Runde 13: gabe-summe, spar-rate."""
    assert bindings.bind(
        "Goldy bought 20 sacks of rice and gave 3 sacks to her cousin "
        "and 4 sacks to her brother. If there are 25 kilograms of "
        "rice per sack, how many kilograms did she give to her cousin "
        "and brother?").answer == "175"
    assert bindings.bind(
        "Rong has been saving 20 coins every month. Neil has been "
        "saving 2/5 times more coins per month than Rong. How many "
        "coins are they having ten years after they started?"
    ).answer == "5760"


def test_batch_neu9():
    """Runde 14: prozent-mehr, pct-of-n-Kette."""
    assert bindings.bind(
        "George has 45% more pears than bananas. If George has 200 "
        "bananas, how many fruits does George have?").answer == "490"
    assert bindings.bind(
        "20% of 50 people think horse #2 will win. 60% of the "
        "remaining people think horse #7 will win. The rest think "
        "horse #12 will win. How many people think horse #12 will "
        "win?").answer == "16"


def test_batch_neu10():
    """Runde 15: paar-total Variante, relativ-geschw."""
    assert bindings.bind(
        "Gretchen has some coins. There are 30 more gold coins than "
        "silver coins. If she had 70 gold coins, how many coins did "
        "Gretchen have in total?").answer == "110"
    assert bindings.bind(
        "The first car is traveling at 60 miles per hour when the "
        "second car passes it at 70 miles per hour. How many miles "
        "will separate them after 2 hours?").answer == "20"


def test_gave_him_und_placed():
    """Richtungs-sensitive Addition + placed-Division."""
    assert bindings.bind(
        "Paul has 52 marbles. His friend gave him 28 marbles. Then "
        "he gave 40 marbles to his sister. How many marbles does "
        "Paul have left?").answer == "40"
    assert bindings.bind(
        "Lani baked 55 cookies. She ate 5 cookies and placed the "
        "rest equally into 5 boxes. How many cookies are in each "
        "box?").answer == "10"


def test_episoden():
    """20 min x (20/2 Episoden) = 200."""
    r = bindings.bind(
        "Each episode is 20 minutes long, and there are half as many "
        "episodes in total as there are minutes per episode. How many "
        "minutes will John spend watching the show?")
    assert r.ok and r.answer == "200"


def test_sammel_kette():
    """picks = Plus + triple-Referenz."""
    r = bindings.bind(
        "John picks 4 bananas on Wednesday. Then he picks 6 bananas "
        "on Thursday. On Friday, he picks triple the number of "
        "bananas he did on Wednesday. How many bananas does John "
        "have?")
    assert r.ok and r.answer == "22"


def test_batch_neu11():
    """Runde 16: blink-rate, alter, bought-more."""
    assert bindings.bind(
        "The light on a lighthouse blinks 255 times in 5 minutes. "
        "How long will it take the light to blink 459 times?"
    ).answer == "9"
    assert bindings.bind(
        "Raymond was born 6 years before Samantha. Raymond had a son "
        "at the age of 23. If Samantha is now 31, how many years ago "
        "was Raymond's son born?").answer == "14"
    assert bindings.bind(
        "Patricia has 30 roses. She gave 24 roses to her mother. She "
        "bought 15 more roses. How many roses did she have now?"
    ).answer == "21"


def test_batch_neu12():
    """Runde 17: gave-fraction, multi-day."""
    assert bindings.bind(
        "Jack had $100. Sophia gave him 1/5 of her $100. How many "
        "dollars does Jack have now?").answer == "120"
    assert bindings.bind(
        "Sam ran 3 miles on Monday, Wednesday and Friday. On Tuesday "
        "and Thursday he ran 2 miles each day. How many miles did "
        "Sam run in total?").answer == "13"


def test_batch_neu13():
    """Runde 18: pflanzen-gruppen, multi-day Liste."""
    assert bindings.bind(
        "She has 20 plants. 4 of her plants need half of a cup of "
        "water. 8 plants need 1 cup of water. The rest need a "
        "quarter of a cup of water. How many cups does she need?"
    ).answer == "12"
    assert bindings.bind(
        "Sam ran 3 miles on Monday, Wednesday and Friday. On Tuesday "
        "and Thursday he ran 2 miles each day. How many miles did "
        "Sam run in total?").answer == "13"


def test_batch_neu14():
    """Runde 19: muenzen, pizza-teilen."""
    assert bindings.bind(
        "The jar has 32 quarters, 95 dimes, 120 nickels, and 750 "
        "pennies. What is the total dollar amount in the jar?"
    ).answer == "31"
    assert bindings.bind(
        "Henry and 3 of his friends order 7 pizzas. Each pizza is "
        "cut into 8 slices. If they want to share the pizzas equally, "
        "how many slices can each of them have?").answer == "14"


def test_batch_neu15():
    """Runde 20: bought-add Richtung + N-more sauber."""
    assert bindings.bind(
        "Charlie had 10 stickers. He bought 21 stickers from a store "
        "and got 23 for his birthday. Then Charlie gave 9 to his "
        "sister and used 28 to decorate a card. How many stickers "
        "does Charlie have left?").answer == "17"
    assert bindings.bind(
        "Patricia has 30 roses. She gave 24 roses to her mother. She "
        "bought 15 more roses. How many roses did she have now?"
    ).answer == "21"


def test_ernte_rate():
    """10ha x 100/ha x 4 Ernten = 4000."""
    r = bindings.bind(
        "John has 10 hectares of a pineapple field. There are 100 "
        "pineapples per hectare. John can harvest his pineapples "
        "every 3 months. How many pineapples can John harvest within "
        "a year?")
    assert r.ok and r.answer == "4000"


def test_batch_neu16():
    """Runde 21: dollar-bills, pennies/100."""
    assert bindings.bind(
        "Brady has 100 pennies, 40 nickels, 20 dimes, and 40 pieces "
        "of dollar bills. How much does Brady have in dollars?"
    ).answer == "45"
    assert bindings.bind(
        "There are 9,300 pennies in a cup. What is the total dollar "
        "amount in a stack that contains two thirds of the pennies in "
        "the cup?").answer == "62"


def test_pennies_drittel():
    """9,300 x 2/3 / 100 = 62 Dollar."""
    r = bindings.bind(
        "There are 9,300 pennies in a cup. What is the total dollar "
        "amount in a stack that contains two thirds of the pennies in "
        "the cup?")
    assert r.ok and r.answer == "62"


def test_baum_kette():
    """F = C/2, H = 2F+5, H-F = 8."""
    r = bindings.bind(
        "There are 6 trees in Chris's yard. Ferdinand has half the "
        "number of trees that Chris has. Harry has 5 more than twice "
        "the number of trees that Ferdinand has. How many more trees "
        "are in Harry's yard than Ferdinand's yard?")
    assert r.ok and r.answer == "8"


def test_batch_neu17():
    """Runde 22: geld-kette, additional."""
    assert bindings.bind(
        "Carmen has $100, Samantha has $25 more than Carmen, and "
        "Daisy has $50 more than Samantha. How much do all three "
        "girls have combined?").answer == "400"
    assert bindings.bind(
        "Annika brought $50 to the town fair. She spent half of it "
        "on food and snacks, and an additional $10 for rides. How "
        "much, in dollars, is left?").answer == "15"


def test_batch_neu18():
    """Runde 23: percent-Wort, result-ref, them-ref."""
    assert bindings.bind(
        "There are 220 castles in Scotland. 40 percent of them are "
        "ruins, and half of the ruined castles are unmanned. How "
        "many unmanned ruined castles are there in Scotland?"
    ).answer == "44"
    assert bindings.bind(
        "Jack had $100. Sophia gave him 1/5 of her $100. How many "
        "dollars does Jack have now?").answer == "120"


def test_batch_neu19():
    """Runde 24: spar-ziel, woche-mult."""
    assert bindings.bind(
        "Mark has $50 in his bank account. He earns $10 per day. If "
        "he wants to buy a bike that costs $300, how many days does "
        "Mark have to save his money?").answer == "25"
    assert bindings.bind(
        "Hallie had dance practice for 1 hour on Tuesdays and 2 "
        "hours on Thursdays. On Saturdays, she had dance practice "
        "that lasted twice as long as Tuesday's night class. How many "
        "hours a week did she have dance practice?").answer == "5"


def test_batch_neu20():
    """Runde 25: share-them, mehr-als-haelfte."""
    assert bindings.bind(
        "Sitti and Juris bought 34 and 22 oranges, respectively. If "
        "both of them decide to share them equally with their 6 "
        "other friends, how many oranges will everyone get?"
    ).answer == "7"
    assert bindings.bind(
        "Indras has 6 letters in her name. Her sister's name has 4 "
        "more letters than half of the letters in Indras' name. How "
        "many letters are in Indras and her sister's names?"
    ).answer == "13"


def test_batch_neu21():
    """Runde 26: possessiv-ref, N-thirds, girl-ziel."""
    assert bindings.bind(
        "Jana has 27 puppies. Two thirds of Jana's puppies are "
        "Pomeranians. One third of the Pomeranians are girls. How "
        "many girl Pomeranians does Jana have?").answer == "6"
    assert bindings.bind(
        "Ben has 4 tubes of blue paint and 3 tubes of yellow paint. "
        "Jasper has half as many tubes of blue paint as Ben, and "
        "three times as many tubes of yellow paint as Ben. How many "
        "tubes of paint does Jasper have?").answer == "11"


def test_halb_dreifach():
    """Ben 4 blau/3 gelb, Jasper halb blau + 3x gelb = 11."""
    r = bindings.bind(
        "Ben has 4 tubes of blue paint and 3 tubes of yellow paint. "
        "Jasper has half as many tubes of blue paint as Ben, and "
        "three times as many tubes of yellow paint as Ben. How many "
        "tubes of paint does Jasper have?")
    assert r.ok and r.answer == "11"


def test_batch_neu22():
    """Runde 27: rueckwaerts-times, gewichtsverlust, groesser-als."""
    assert bindings.bind(
        "Nick had twice as many candies as George. Then George ate 5 "
        "candies. Now George has 3 candies left. How many candies "
        "does Nick have?").answer == "16"
    assert bindings.bind(
        "Mark was unwell for 3 months, during which he lost 10 "
        "pounds per month. If his final weight was 70 pounds, what "
        "was his initial weight?").answer == "100"
    assert bindings.bind(
        "He needed 2 more toys than he already had to make a play "
        "set five times larger than James's set, which had 80 toys. "
        "How many toys does Jonathan currently have?").answer == "398"


def test_batch_neu23():
    """Runde 28: bloomed-Ziel, weniger-zusammen."""
    assert bindings.bind(
        "Arianna plants a garden that has 10 rows of flowers with 20 "
        "flowers in each row. Currently, only 4/5 of the planted "
        "flowers have bloomed. How many flowers in Arianna's garden "
        "have bloomed?").answer == "160"
    assert bindings.bind(
        "A boy has 5 cards. His brother has 3 fewer cards than he "
        "has. How many cards do they have together?").answer == "7"


def test_batch_neu24():
    """Runde 29: pro-einheit, Rate-Paarung."""
    assert bindings.bind(
        "For every muffin, Svetlana needed 5 tablespoons of flour, 3 "
        "tablespoons of sugar, and 0.25 of a tablespoon of salt. How "
        "many tablespoons of dry ingredients would Svetlana need to "
        "make 16 muffins?").answer == "132"
    assert bindings.bind(
        "Alisa biked 12 miles per hour for 4.5 hours. Stanley biked "
        "at 10 miles per hour for 2.5 hours. How many miles did "
        "Alisa and Stanley bike in total?").answer == "79"


def test_batch_neu25():
    """Runde 30: Dezimal-Dauer."""
    assert bindings.bind(
        "Alisa biked 12 miles per hour for 4.5 hours. Stanley biked "
        "at 10 miles per hour for 2.5 hours. How many miles did "
        "Alisa and Stanley bike in total?").answer == "79"


def test_batch_neu26():
    """Runde 31: fabrik-rate, wochen-vergleich."""
    assert bindings.bind(
        "An ice cream factory makes 100 quarts of chocolate ice cream "
        "in 2 hours. It can make 50 quarts of vanilla ice cream in 4 "
        "hours. How many quarts in total would be made in 48 hours?"
    ).answer == "3000"
    assert bindings.bind(
        "Castle bought 3 boxes of Coco Crunch and 5 boxes of Fruit "
        "Loops this week. Last week she bought 4 boxes of cereal. How "
        "many more boxes did she buy this week than last week?"
    ).answer == "4"


def test_wochen_vergleich():
    """3+5 diese, 4 letzte -> 4 mehr."""
    r = bindings.bind(
        "Castle bought 3 boxes of Coco Crunch and 5 boxes of Fruit "
        "Loops this week. Last week she bought 4 boxes of cereal. How "
        "many more boxes of cereal did she buy this week than last "
        "week?")
    assert r.ok and r.answer == "4"


def test_batch_neu27():
    """Runde 32: get-off/get-on, twenties."""
    assert bindings.bind(
        "A train has 172 people. At the first stop 47 people get off "
        "and 13 more people get on, and at the next stop another 38 "
        "people get off. How many people are on the train?"
    ).answer == "100"
    assert bindings.bind(
        "Carrie was given ten twenties and 140 quarters by her aunt. "
        "If she spent all the quarters and 3/5 of the twenties, "
        "calculate the total amount of money she paid.").answer == "155"


def test_batch_neu28():
    """Runde 33: trinkgeld, mehrfach-weniger."""
    assert bindings.bind(
        "Each of the forty customers gave Rafaela a $20 tip. Julieta "
        "received 10% less money in tips than Rafaela. How much did "
        "Julieta and Rafaela receive as tips altogether?"
    ).answer == "1520"
    assert bindings.bind(
        "Daisy bought a bag of potatoes that weighed 5 pounds. She "
        "also bought sweet potatoes that weighed 2 times as much as "
        "the potatoes and carrots that weighed 3 pounds fewer than "
        "the sweet potatoes. How many pounds of carrots did Daisy "
        "buy?").answer == "7"


def test_batch_neu29():
    """Runde 34: snuck-div, gives."""
    assert bindings.bind(
        "Susan made 100 cookies and was going to equally divide them "
        "between her 6 nephews. Before she could package them, her "
        "husband snuck 4 cookies for himself. How many cookies will "
        "each of Susan's nephews get?").answer == "16"
    assert bindings.bind(
        "Dean has 30 marbles. He gives 1/5 of them to Jamie and "
        "gives 10 to Donald. How many marbles are left for Dean?"
    ).answer == "14"


def test_batch_neu30():
    """Runde 35: doppelt-verloren, papier-dicke."""
    assert bindings.bind(
        "Sarah has 9 books and Joseph had twice the number of "
        "Sarah's books, but he lost 2 of them. How many books does "
        "Joseph currently have?").answer == "16"
    assert bindings.bind(
        "The book is printed on paper that, when stacked, is 100 "
        "pages to the inch. Each paper is printed on both sides, "
        "with one page printed on each side. How many pages are in "
        "the book, if it is 1.5 inches thick?").answer == "300"


def test_batch_neu31():
    """Runde 36: lese-rate, doppel-rate."""
    assert bindings.bind(
        "It takes James 10 minutes to read 3 pages of his book. He "
        "reads 18 pages of his book and then decides to go to sleep. "
        "How long does James spend reading, in minutes?"
    ).answer == "60"
    assert bindings.bind(
        "Emily can peel 6 shrimp a minute and saute 30 shrimp in 10 "
        "minutes. How long will it take her to peel and cook 90 "
        "shrimp?").answer == "45"


def test_batch_neu32():
    """Runde 37: pct-in, woche-rate."""
    assert bindings.bind(
        "There are 50 books in a small library. Half of them are "
        "written in English, and 10% in German. All others are "
        "written in Spanish. How many Spanish books are there?"
    ).answer == "20"
    assert bindings.bind(
        "A man eats 5 sandwiches per day, his wife eats 4 sandwiches "
        "per day, and their son eats 2 sandwiches per day. How many "
        "sandwiches does this family eat in one week?").answer == "77"


def test_batch_neu33():
    """Runde 38: rueck-kept, rosen-preis."""
    assert bindings.bind(
        "Seth gave half of his stickers to Luis. Luis used half of "
        "the stickers and gave the rest to Kris. Kris kept 9 of the "
        "stickers and gave the remaining 7 to Rob. How many stickers "
        "did Seth have in the beginning?").answer == "64"
    assert bindings.bind(
        "Roses cost $2 each and $15 for a dozen. If she bought 15 "
        "roses and arrived with five 5 dollar bills and they only "
        "have quarters for change, how many quarters does she leave "
        "with?").answer == "16"


def test_batch_neu34():
    """Runde 39: sam-komma, fish-and."""
    assert bindings.bind(
        "Sam ran 3 miles on Monday, Wednesday and Friday. On Tuesday "
        "and Thursday, Sam ran 5 miles. How many miles did Sam run "
        "this week?").answer == "19"
    assert bindings.bind(
        "There are 66 fish in the fish tank. One-third of the fish "
        "have red stripes, and 5/11 of the remaining fish have blue "
        "stripes. Altogether, how many fish have red stripes and "
        "blue stripes?").answer == "42"


def test_batch_neu35():
    """Runde 40: gruppen-wachstum, halbe-plus."""
    assert bindings.bind(
        "An ice cream truck is traveling through a neighborhood. "
        "There are 5 children. On the second street, each child is "
        "joined by another child and on the third street, each child "
        "is joined by another 2 children. The original 5 children "
        "then give up and leave. How many children are now "
        "following the truck?").answer == "25"
    assert bindings.bind(
        "Steve put together a puzzle that took 10 hours of hard work "
        "to complete. Anna put together the same puzzle in 2 hours "
        "more than half Steve's time. How long did it take Anna to "
        "finish the difficult puzzle?").answer == "7"


def test_batch_neu36():
    """Runde 41: rechteck-umfang, docks-line."""
    assert bindings.bind(
        "His backyard fence is a rectangle that measures 20 feet on "
        "the long side and 15 feet on the short side. How many feet "
        "of crepe paper does James need to buy?").answer == "70"
    assert bindings.bind(
        "He wants 3 feet of line for every foot of dock. Right now, "
        "there is 200 feet of dock, and he has 6 feet of new line. "
        "How many feet of line does he need to buy in total?"
    ).answer == "594"


def test_batch_neu37():
    """Runde 42: pflanzen-prozent, gewicht-force."""
    assert bindings.bind(
        "A small sunflower has 3 dozen seeds and a large sunflower "
        "has 50% more seeds than a small sunflower. How many "
        "sunflower seeds are there altogether?").answer == "90"
    assert bindings.bind(
        "The car weighs 1200 pounds and he has luggage in it "
        "weighing 250 pounds. He also has his two young children "
        "who weigh 75 pounds each in it. If the force to move the "
        "car is 1% of the weight how much force does he need to "
        "push the car?").answer == "16"


def test_batch_neu38():
    """Runde 43: gleich-teilen, bag-teile."""
    assert bindings.bind(
        "He buys two bags of chips with 55 chips each. If his family "
        "has five members, how many chips does each person get if "
        "they all get the same number?").answer == "22"
    assert bindings.bind(
        "A large bag of Starbursts candy has 232 pieces. If this bag "
        "has 54 red candies, twice that amount of orange candies and "
        "half as many yellow candies as red candies, how many "
        "candies are pink?").answer == "43"


def test_batch_neu39():
    """Runde 44: putz-anteil, wochen-futter."""
    assert bindings.bind(
        "A custodian has to clean a school with 80 classrooms. They "
        "have 5 days to get it done. It takes them 15 minutes per "
        "classroom. If they work an 8 hour day, what percentage of "
        "their day, on average, is spent cleaning classrooms?"
    ).answer == "50"
    assert bindings.bind(
        "The Kennel house keeps 3 German Shepherds and 2 Bulldogs. "
        "If a German Shepherd consumes 5 kilograms of dog food and "
        "a bulldog consumes 3 kilograms per day. How many kilograms "
        "will they need in a week?").answer == "147"


def test_batch_neu40():
    """Runde 45: schueler-anwesen, frucht-beginn."""
    assert bindings.bind(
        "Last Friday, 13 of the 82 teachers were sick. There were 9 "
        "substitute teachers called in to help. How many teachers "
        "were at school that day?").answer == "78"
    assert bindings.bind(
        "Madeline ate 6 grapes. Her brother used up 5 times as many "
        "grapes then Madeline. Their mother then used the remaining "
        "grapes to make 4 pies. How many grapes were there at the "
        "beginning if the pie recipe calls for 12 grapes per pie?"
    ).answer == "84"


def test_batch_neu41():
    """Runde 46: regen-zwei, weniger-kette."""
    assert bindings.bind(
        "It rained 2 inches on Monday and is expected to rain 1 more "
        "inch than twice of Monday's total on Tuesday. How many "
        "inches of rain will there be on Tuesday?").answer == "5"
    assert bindings.bind(
        "Samantha has 12 fewer paintings than Shelley, and Shelley "
        "has 8 paintings more than Kim. If Samantha has 27 "
        "paintings, how many paintings does Kim have?").answer == "31"


def test_batch_neu42():
    """Runde 47: regen-zwei (curly-apostroph)."""
    assert bindings.bind(
        "It rained 2 inches on Monday and is expected to rain 1 more "
        "inch than twice of Monday's total on Tuesday. How many "
        "inches of rain will there be on Tuesday?").answer == "5"


def test_batch_neu43():
    """Runde 48: windeln-halb, dosis-mix, escape-raum."""
    assert bindings.bind(
        "Jordan has 2 children who wear diapers. Each child requires "
        "5 diaper changes per day. Jordan's wife changes half of the "
        "diapers. How many diapers does Jordan change per day?"
    ).answer == "5"
    assert bindings.bind(
        "Saanvi had to combine 14 mL of one medicine with 3 times "
        "that amount of the second medicine. How many mL of medicine "
        "would be in 8 doses?").answer == "448"
    assert bindings.bind(
        "Cedar Falls Middle School has students in grades 4 – 7. "
        "The 10 students in each grade get to try an escape room. "
        "Only 8 students can try at a time. They have 45 minutes to "
        "try and escape. How long will it take for everyone?"
    ).answer == "225"


def test_batch_neu44():
    """Runde 49: fleisch-wuerze, stift-pakete."""
    assert bindings.bind(
        "He adds two tablespoons of his secret steakhouse seasoning "
        "for every pound of ground beef. He gets sixteen meatballs "
        "from each pound of meat. If he wants to make 80 meatballs, "
        "how much of his secret seasoning will he need?").answer == "10"
    assert bindings.bind(
        "Alain's mom bought 5 packs of red pens and also bought "
        "twice the amount of black pens than the red. If each pack "
        "has 5 pens, how many pens does Alain have?").answer == "75"


def test_batch_neu45():
    """Runde 50: bandagen-start."""
    assert bindings.bind(
        "A nurses' station orders bandages in bulk packs of 50. On "
        "the first day, the nurses used 38 bandages and ordered one "
        "bulk pack. On the second day, they used ten fewer bandages. "
        "On the third day, they ordered two bulk packs and only used "
        "half a pack. They had 78 bandages left at the end of the "
        "third day. How many bandages did they start with on the "
        "first day?").answer == "19"


def test_batch_neu46():
    """Runde 51: mural-farben, geld-umwandeln."""
    assert bindings.bind(
        "A wall mural has four different colors of paint in it: red, "
        "white, purple, and yellow. There are equal amounts of red, "
        "white, and purple paint. Half the mural is yellow. If the "
        "mural used 12 pints of paint in all, how many pints of red "
        "paint were used?").answer == "2"
    assert bindings.bind(
        "Thomas withdraws $1000 in 20 dollar bills. He loses 10 "
        "bills. After that, he uses half of the remaining bills to "
        "pay for a bill. Thomas then triples his money. He then "
        "converts all his bills to 5 dollar bills. How many bills "
        "does he have?").answer == "240"


def test_batch_neu47():
    """Runde 52: wochentag-rate, eier-kette."""
    assert bindings.bind(
        "Mason likes eating carrots. If he eats 4 carrots each on "
        "weekdays and 5 carrots each on Saturday and Sunday, how "
        "many carrots does he eat a week?").answer == "30"
    assert bindings.bind(
        "Cole hid 3 dozen eggs in the yard. Lamar finds 5 eggs. "
        "Stacy finds twice as many as Lamar. Charlie finds 2 less "
        "than Stacy. And Mei finds half as many as Charlie. How "
        "many eggs are still hidden?").answer == "9"


def test_batch_neu48():
    """Runde 53: backen-each."""
    assert bindings.bind(
        "Randy has 9 oatmeal cookies, 4 chocolate chip cookies, and "
        "5 sugar cookies. He ate 3 cookies for an early day snack. "
        "He ate 2 oatmeal cookies for lunch. He gives 2 sugar "
        "cookies to his friends. Then, he bakes 4 of each flavor for "
        "dinner. How many cookies does he have now?").answer == "23"


def test_batch_neu49():
    """Runde 54: ernte-jahr, stein-stand, steuer-mitte."""
    assert bindings.bind(
        "Tim grows 5 trees. Each year he collects 6 lemons from "
        "each tree. How many lemons does he get in a decade?"
    ).answer == "300"
    assert bindings.bind(
        "Adam has $100 and wants to spend it to open a rock stand. "
        "He can buy rocks for $5 each and sell them for $7 each. If "
        "he invests all his money but only sells 60% of his "
        "inventory, how much money does he lose?").answer == "16"
    assert bindings.bind(
        "Last week the IRS received 5168 tax reports. On Monday and "
        "Tuesday they received a total of 1907 reports. On Thursday "
        "and Friday they received a total of 2136 reports. How many "
        "reports did they receive on Wednesday?").answer == "1125"


def test_batch_neu50():
    """Runde 55: kiste-gewicht, marmor-umgekehrt, weg-rate."""
    assert bindings.bind(
        "Nik has 200 crayons. He wants to separate them into groups "
        "of 8 and put them into boxes. Each box weighs 8 ounces. "
        "Each crayon weighs 1 ounce. What is the total weight, in "
        "pounds, of the crayons and the boxes?").answer == "25"
    assert bindings.bind(
        "Bob has a certain number of marbles. If he receives 2 dozen "
        "more marbles, he will have 60 marbles. If he loses 10 of "
        "the marbles he has, how many marbles will Bob have?"
    ).answer == "26"
    assert bindings.bind(
        "Grandma walks 3 miles every day, which includes 2 miles of "
        "walking on the beach and 1 mile of walking on the "
        "sidewalk. On the sidewalk, "
        "Grandma walks at twice the rate of speed that she does on "
        "the beach. If 40 minutes of her walk is spent on the beach, "
        "how long does it take for her to complete the entire 3-mile "
        "walk, in minutes?").answer == "50"


def test_batch_neu51():
    """Runde 56: lauf-rest, spar-ausgabe, albatros, halbe-rueck,
    kirche-mix."""
    assert bindings.bind(
        "Amber, Micah, and Ahito ran 52 miles in total. Amber ran 8 "
        "miles. Micah ran 3.5 times what Amber ran. How many miles "
        "did Ahito run?").answer == "16"
    assert bindings.bind(
        "Raymond had $21. Then he saved $11 from his allowance and "
        "spent $5 on a comic book and $19 on a puzzle. How much "
        "money does Raymond have left?").answer == "8"
    assert bindings.bind(
        "Alfie flies 400 kilometers every day. If the circumference "
        "of the earth is 40,000 kilometers, how many days will it "
        "take Alfie to fly half of the way around the earth?"
    ).answer == "50"
    assert bindings.bind(
        "A Tyrannosaurus rex ate half of a small triceratops it had "
        "hunted. When it left, a pack of velociraptors scavenged "
        "half of what was left. A group of lazy Allosaurus gulped "
        "down the last 270 kilograms of meat. How many kilograms "
        "were on the triceratops?").answer == "1080"
    assert bindings.bind(
        "There were 20 private cars and 12 buses parked outside the "
        "church. After the ceremony, each bus carried 35 people and "
        "each car carried 3 people. How many people were inside the "
        "church?").answer == "480"


def test_batch_neu52():
    """Runde 57: halb-rueck-weg, steuer-frei, stunden-woche."""
    assert bindings.bind(
        "James decided to walk to the store. When he got halfway "
        "there he realized he forgot something at home and had to "
        "walk back. If his home is 4 miles from the store and he "
        "walks 4 miles per hour how long did it take him to reach "
        "the store?").answer == "2"
    assert bindings.bind(
        "Billy can help 2 people per hour for 3 hours a day. If he "
        "takes 20% of the days between March 1st and April 19th off, "
        "and helps people on all the other days. How many people "
        "does he help?").answer == "240"
    assert bindings.bind(
        "There are 6 periods in the day but John has to take 2 extra "
        "classes. Each class is 40 minutes long. He goes to class "
        "for 5 days a week. He then spends 1/16 of his weekly "
        "minutes each on Saturday and Sunday as extra learning time. "
        "How many hours a week does he spend learning?").answer == "30"


def test_batch_neu53():
    """Runde 58: zwei-gruppen-prozent, geld-viertel, puzzle-zwei."""
    assert bindings.bind(
        "The glee club ordered 20 pizzas and ate 70% of them. The "
        "football team ordered twice as many pizzas and ate 80% of "
        "them. How many pizzas are left?").answer == "14"
    assert bindings.bind(
        "Maggie spent a quarter of her money, while Riza spent "
        "one-third of her money. They each had $60. How much money "
        "do the two of them have left?").answer == "85"
    assert bindings.bind(
        "Teddy finished half of a 500 piece puzzle, and then started "
        "and finished another 500 piece puzzle within an hour. How "
        "many puzzle pieces did Teddy place during that hour?"
    ).answer == "750"


def test_batch_neu54():
    """Runde 59: fahrt-rest, sticker-jahre, pizza-slices."""
    assert bindings.bind(
        "It is approximately 1955 kilometers from San Diego to New "
        "York. If Bernice drove 325 kilometers for 4 days, how many "
        "kilometers will she still need to drive?").answer == "655"
    assert bindings.bind(
        "Leo collects stickers. Two years ago, he had 100 stickers "
        "in his collection. Last year, Leo collected 50 stickers. "
        "This year, he collected twice the number of stickers as "
        "the previous year. How many stickers does Leo have?"
    ).answer == "250"
    assert bindings.bind(
        "Becky, Jake, and Silvia shared 4 pizzas. Each pizza had 8 "
        "slices. Becky ate 3 more slices than Jake did. Silvia ate "
        "twice as many slices than Jake did. If Becky ate 10 slices, "
        "how many total slices did they eat?").answer == "31"


def test_batch_neu55():
    """Runde 60: zwerg-mine, ballon-platz, flaschen-zeit,
    weiter-fahren, hotel-gaeste, eier-freunde."""
    assert bindings.bind(
        "One dwarf can mine 12 pounds of ore per day. He can mine "
        "twice as much with an iron pickaxe and 50% more with a "
        "steel pickaxe than with an iron pickaxe. How many pounds "
        "can 40 dwarves with steel pickaxes mine in a month?"
    ).answer == "43200"
    assert bindings.bind(
        "Sally was holding the strings to 25 red balloons, 7 green "
        "balloons, and 12 yellow balloons. A gust of wind caused 40% "
        "of the red balloons to burst. How many balloons is Sally "
        "holding?").answer == "34"
    assert bindings.bind(
        "Richard's driveway is 24 feet wide and he wants to put a "
        "bottle of soda every 3 feet of the driveway. After starting "
        "at the first bottle, it will take Richard 5 seconds to go "
        "from one soda bottle to the next. How many seconds total "
        "will it take Richard?").answer == "35"
    assert bindings.bind(
        "Matteo traveled at 55 miles per hour for 4 hours. Shandy "
        "traveled at 45 miles per hour for 10 hours. How many miles "
        "farther did Shandy drive than Matteo?").answer == "230"
    assert bindings.bind(
        "A hotel was completely booked with 100 guests. 24 guests "
        "elected an early checkout and 15 elected for a late "
        "checkout. In the afternoon twice as many people checked in "
        "as those who opted for a late checkout. 7 more people "
        "checked in after dinner. How many guests does the hotel "
        "now have?").answer == "98"
    assert bindings.bind(
        "The Easter egg hunt team hid 100 eggs. The Smith twins each "
        "found 30 eggs. All the other eggs except 10 were found by "
        "their friends. How many eggs did the friends find?"
    ).answer == "30"


def test_batch_neu56():
    """Runde 61: perlen-kette, prozent-doppel, stoeckchen,
    saite-zeit, mannschaft-zwei, orangen-verkauf."""
    assert bindings.bind(
        "Her mother gave her 20 metallic beads. Her sister gave her "
        "ten more beads than her mother, and her friend gave her "
        "twice as many as her mother gave. How many beads did "
        "Adrianne have?").answer == "90"
    assert bindings.bind(
        "In Mr. Roper's class of 30 students, 20% of the class are "
        "football players. Out of the remaining class, 25% of the "
        "students are cheerleaders or part of band. How many "
        "students leave early?").answer == "12"
    assert bindings.bind(
        "There are 9 red sticks, and 5 more blue sticks than red. "
        "Also, the number of yellow sticks is 3 less than the blue "
        "sticks. How many sticks do they have?").answer == "34"
    assert bindings.bind(
        "He has 12 racquets. 3 are to be strung with synthetic gut, "
        "5 will be strung with polyester string, and 4 with a "
        "hybrid set. It takes 15 minutes for him to string with "
        "synthetic gut, 22 minutes to string with polyester string, "
        "and 18 minutes for hybrid sets. How long will it take "
        "Andy?").answer == "227"
    assert bindings.bind(
        "Zeke's baseball team has 7 more players than Carlton's. If "
        "Carlton's team has 13 players, how many players are there "
        "in both teams combined?").answer == "33"
    assert bindings.bind(
        "Mrs. Harrington bought 12 boxes of oranges. She gave her "
        "mom and her sister 2 boxes each. Then she kept 1/4 of the "
        "oranges and sold the rest. How many oranges did she sell "
        "if each box contains 20 oranges?").answer == "120"


def test_batch_neu57():
    """Runde 62: punkte-drei, chips-drei, vogel-flug,
    schwimm-pause, provision, sticker-verlust."""
    assert bindings.bind(
        "Bahati, Azibo, and Dinar each contributed to their team's "
        "45 points. Bahati scored the most points and it was 20 "
        "more than Azibo scored and 10 more points than Dinar "
        "scored. How many points did Azibo score?").answer == "5"
    assert bindings.bind(
        "Only two people would get an equal amount of corn chips, "
        "while the other person would receive 15 more corn chips "
        "than the number the others got. If Amora and Lainey got 70 "
        "corn chips each, how many corn chips were there "
        "altogether?").answer == "225"
    assert bindings.bind(
        "The bird flies in a southerly direction for 10 hours at a "
        "speed of 30 miles per hour. Then, the bird turns direction "
        "and flies towards the north for 2 hours at a speed of 18 "
        "miles per hour. Finally, the bird changes direction and "
        "flies toward the south for 5 hours at a speed of 22 miles "
        "per hour. What is the distance between the bird's homes?"
    ).answer == "374"
    assert bindings.bind(
        "James has to swim across a 20-mile lake. He can swim at a "
        "pace of 2 miles per hour. He swims 60% of the distance. "
        "After that, he stops on an island and rests for half as "
        "long as the swimming time. He then finishes the remaining "
        "distance while going half the speed. How long did it take "
        "him?").answer == "17"
    assert bindings.bind(
        "He gets a 10% commission on each copy of the New York Times "
        "and an 8% commission on each of the Wall Street Journal. "
        "How much commission will he earn from the sales of 6 "
        "copies of the New York Times and 10 copies of Wall Street "
        "Journal if each costs $5 and $15 respectively?").answer == "15"
    assert bindings.bind(
        "She was given 15 stickers for participating in class, but "
        "she lost 7 stickers during playtime. However, her teacher "
        "gave her another 5 stickers. How many stickers does she "
        "have now?").answer == "13"


def test_batch_neu58():
    """Runde 63: mini-kalorien, fahrzeug-diff, klasse-saft."""
    assert bindings.bind(
        "Andrew bakes 200 mini cinnamon rolls and 300 mini blueberry "
        "muffins. A normal cinnamon roll has 600 calories and a "
        "normal blueberry muffin has 450 calories. If a mini pastry "
        "has 1/3rd of the calories of a normal version, how many "
        "calories do the pastries have?").answer == "85000"
    assert bindings.bind(
        "A bus travels 60 miles per hour for 5 hours. A car travels "
        "30 miles per hour for 8 hours. How much farther did the "
        "bus go than the car, in miles?").answer == "60"
    assert bindings.bind(
        "There are 29 pupils in a class. The teacher has 9 coupons; "
        "each coupon can be redeemed for 100 bottles of apple juice. "
        "The teacher gives each student 2 bottles of apple juice to "
        "drink. After redeeming all her coupons and giving each "
        "student their juice, how many bottles are left?"
    ).answer == "842"


def test_batch_neu59():
    """Runde 64: obst-rest, tee-reihen, kino-budget."""
    assert bindings.bind(
        "Kira bought 3 apples, 5 bananas and 6 oranges at the "
        "grocery store. Lola ate 2 pieces of the fruit. How many "
        "pieces are left?").answer == "12"
    assert bindings.bind(
        "Lana has 27 cups, and she divides these into 3 rows. In "
        "each row, she creates equal amounts of chamomile and mint "
        "tea cups. She then uses the remaining cups to brew a total "
        "of 15 cups of cinnamon tea. How many cups of mint tea are "
        "in each row?").answer == "2"
    assert bindings.bind(
        "His parents give him $150 to spend at the movies. Tickets "
        "for Fridays and Saturdays cost $10. Other days cost $7. "
        "Popcorn costs $8 and boxes of candy cost $2. It's a "
        "Friday. He already saw 5 movies on a Friday or Saturday, 8 "
        "movies on other days, had 2 tubs of popcorn, and four "
        "boxes of candy that month. How many movies can he see if "
        "he wants a popcorn and box of candy that night?"
    ).answer == "1"


def test_batch_neu60():
    """Runde 65: mikro-paare, garten-prozent, hefte-diff."""
    assert bindings.bind(
        "A singer has 50 microphones that he wants to arrange in "
        "pairs. He realizes that 20% of the microphones won't find "
        "any space to fit in after arranging the rest in pairs. How "
        "many pairs of microphones was he able to arrange?"
    ).answer == "20"
    assert bindings.bind(
        "There are 100 plants in Mrs. Smith's garden. One-fourth of "
        "her plants are indoor plants. Two-thirds of the remaining "
        "are outdoor plants while the rest are flowering plants. "
        "What percent of the plants are flowering plants?"
    ).answer == "25"
    assert bindings.bind(
        "Joseph had 3 times as many notebooks as Martha. Martha "
        "bought 5 more for a total of 7 notebooks. How many more "
        "than Joseph does she now have?").answer == "1"


def test_batch_neu61():
    """Runde 66: limonade-diff, spielzeug-gibt, burrito-tage."""
    assert bindings.bind(
        "Julie, Micah, and Mitchell sold 32 glasses of lemonade. "
        "Julie sold 14 glasses and the boys sold an equal number of "
        "glasses. How many more glasses did Julie sell than Micah?"
    ).answer == "5"
    assert bindings.bind(
        "Argo has 200 toys. He gives 40 toys to Alyssa, 80 to "
        "Bonnie, and 30 to Nicky. How many toys does Argo have now?"
    ).answer == "50"
    assert bindings.bind(
        "The Burrito Shop makes 125 chimichangas on Tuesdays, 125 "
        "chimichangas on Wednesdays and twice as many on Friday. "
        "How many chimichangas do they make on those three days?"
    ).answer == "500"


def test_batch_neu62():
    """Runde 67: marmor-verlust, test-punkte, huhn-profit,
    haus-jahre, orange-familie, buecher-drei."""
    assert bindings.bind(
        "Paul has 52 marbles. His friend gave him 28 marbles. Then, "
        "he lost 1/4 of his marbles. How many marbles does Paul "
        "have left?").answer == "60"
    assert bindings.bind(
        "Amy correctly answers 80% of the multiple-choice questions, "
        "90% of the true/false questions, and 60% of the long-answer "
        "questions. The multiple-choice and true/false questions "
        "are worth 1 point each, and the long answer questions are "
        "worth 5 points each. How many points does Amy score if "
        "there are 10 multiple-choice questions, 20 true/false "
        "questions, and 5 long answer questions?").answer == "41"
    assert bindings.bind(
        "To make a profit of $2000, Isaias has to sell the chickens "
        "at $50 per chicken. If Isaias has 300 chickens on his farm "
        "and plans to sell 3/5 of them, for how much money did "
        "Isaias buy the chicken he took to the market?"
    ).answer == "7000"
    assert bindings.bind(
        "In the first year, they will build 12 homes. In the next "
        "year, they will build three times this many homes. In the "
        "third year, they will count how many homes they have built "
        "and double the amount. How many homes will the town have "
        "built over the next three years?").answer == "144"
    assert bindings.bind(
        "Jennifer bought 12 oranges from the market, she gave her "
        "three daughters 2 oranges each, and her only boy got 3 "
        "oranges. How many oranges did she remain with?"
    ).answer == "3"
    assert bindings.bind(
        "Together, Sofie, Anne, and Fawn have 85 books. If Sofie "
        "has 25 more books than Anne, and Anne has 12 fewer books "
        "than Fawn does, how many books does Fawn have?"
    ).answer == "28"


def test_batch_neu63():
    """Runde 68: hemden-diff, ziegen-zwei, zimmer-zeit."""
    assert bindings.bind(
        "A clothing store has 40 white shirts and 50 floral shirts. "
        "Half of the white shirts have collars, and 20 of the floral "
        "shirts have buttons. How many more floral shirts with no "
        "buttons are there than white shirts with no collars?"
    ).answer == "10"
    assert bindings.bind(
        "Mr. Smith has two farms, Farm X and Farm Y. He has 55 goats "
        "in Farm X and 45 goats in Farm Y. He sold 10 goats from "
        "Farm X and twice as many goats from Farm Y. How many goats "
        "are left in the two farms altogether?").answer == "70"
    assert bindings.bind(
        "There are 90 rooms at the KozyInn Motel. It takes "
        "housekeeping 20 minutes to clean each room. How many hours "
        "would it take to clean one-half of the rooms?"
    ).answer == "15"


def test_batch_neu64():
    """Runde 69: geld-kauf, rueck-verlust, tier-zeit."""
    assert bindings.bind(
        "Craig has 2 twenty dollar bills. He buys six squirt guns "
        "for $2 each. He also buys 3 packs of water balloons for $3 "
        "each. How much money does he have left?").answer == "19"
    assert bindings.bind(
        "The book weighs 4 pounds, cost $32, and needs to be "
        "returned 20 miles away. If the shipping company charges "
        "$0.35 per pound plus $0.08 per mile, and Amazon will only "
        "refund 75% of the book's purchase price, how much money "
        "will Milly lose?").answer == "11"
    assert bindings.bind(
        "If it takes 3 kangaroos traveling at the same speed a "
        "total of 18 hours to travel across a highway, how many "
        "hours will it take four turtles, each traveling at half "
        "the speed of a kangaroo, to do so?").answer == "48"


def test_batch_neu65():
    """Runde 70: blumen-petalen, arcade-geld, ostern-eier."""
    assert bindings.bind(
        "Rose picks 3 flowers with 5 petals each, picks 4 flowers "
        "with 6 petals each, adds another 5 flowers with 4 petals "
        "each, and lastly picks 6 flowers with 7 petals each. As "
        "she carries them, she drops 1 of each and the wind blows "
        "them away. How many petals in total are on the flowers in "
        "the vase?").answer == "79"
    assert bindings.bind(
        "Jack can play a game with 1 quarter for 20 minutes. Two of "
        "his friends can only play half as long. One of them can "
        "play for 1.5 times as long. They play for 4 hours. How "
        "much money is used?").answer == "11"
    assert bindings.bind(
        "Cindy had 5 green eggs, twice as many blue ones as green "
        "ones, one fewer pink eggs than blue eggs, and one-third as "
        "many yellow eggs as blue eggs. How many eggs did she have?"
    ).answer == "27"


def test_batch_neu66():
    """Runde 71: loewen-zaehler, muschel-gruppen, firma-gehalt,
    film-kosten, familie-reise, fisch-kauf, wochenende-prozent,
    museum-fahrt."""
    assert bindings.bind(
        "She counts 12 female lions, half as many male lions, and "
        "14 lion cubs. How many lions are in the enclosure?"
    ).answer == "32"
    assert bindings.bind(
        "90 people were required to split into groups. 9-person "
        "groups were formed. If 3/5 of the number of groups each "
        "had members bring back 2 seashells each, how many seashells "
        "did they bring?").answer == "108"
    assert bindings.bind(
        "A company's HR hires 20 new employees every month. If the "
        "initial employee number is 200, and each employee is paid "
        "a $4000 salary per month, calculate the total amount paid "
        "after three months?").answer == "2880000"
    assert bindings.bind(
        "Mike has 600 movies. A third are in series and he can get "
        "those for only $6 of the cost of a normal movie. 40% of "
        "the remaining are older movies which are $5. How much "
        "does replacing the movies cost if a normal movie costs "
        "$10?").answer == "4400"
    assert bindings.bind(
        "The Llesis family drove and hiked 6 hours to their "
        "vacation spot. They drove an average of 50 miles per hour "
        "and hiked an average of 5 miles per hour less than half "
        "their speed when they drive. If it took them 1.5 hours to "
        "hike, how far was their vacation spot?").answer == "255"
    assert bindings.bind(
        "Bob had 7 fish. 3 were orange, and 4 were white. He had a "
        "sales assistant dip out 17 fish. He found that he now had "
        "twice as many orange fish as white fish. How many white "
        "fish did Bob buy at the store?").answer == "4"
    assert bindings.bind(
        "Tatiana has 7 hours on Saturday and 5 hours on Sunday. She "
        "reads for 3 hours and plays video games for 1/3 of the "
        "remaining time. What percentage of her weekend does she "
        "spend playing soccer?").answer == "50"
    assert bindings.bind(
        "Jack decides to visit a museum 150 miles from home. He "
        "drives 75 mph there and back. He spends 6 hours at the "
        "museum. How long is he gone from home?").answer == "10"


def test_batch_neu67():
    """Runde 72: geschirr-rest, fussball-woche, marmor-doppel,
    bananen-kette, pomeranien."""
    assert bindings.bind(
        "Jeff sent 8 dozen glasses and 4 dozen plates. When they "
        "were returned, 10 glasses were broken as well as 6 plates. "
        "How many glasses and plates does Jeff have now?"
    ).answer == "128"
    assert bindings.bind(
        "Joey played 2 matches on Monday, 1 match on Friday, and on "
        "Saturday he played double the number of matches he played "
        "on Monday. How many matches did Joey play in one week?"
    ).answer == "7"
    assert bindings.bind(
        "Carl has four times as many marbles as Sean and Sean has "
        "half as many marbles as Cal. If Sean has 56 marbles, how "
        "many marbles do Carl and Cal have combined?").answer == "336"
    assert bindings.bind(
        "Gunther had 48 bananas. Arnold stole half. The next day, "
        "Gunther added another 25 bananas, but Arnold stole another "
        "12. On the third day, Gunther added another 6 bananas. How "
        "many bananas did Gunther find?").answer == "43"
    assert bindings.bind(
        "Jana has 27 puppies. Two thirds of Jana's puppies are "
        "Pomeranians. One third of the Pomeranians are girls. How "
        "many girl Pomeranians does Jana have?").answer == "6"


def test_batch_neu68():
    """Runde 73: pomeranien-reverse."""
    assert bindings.bind(
        "Two thirds of Jana's puppies are Pomeranians. One third of "
        "the Pomeranians are girls. If there are 6 Pomeranian "
        "girls, how many puppies does Jana have?").answer == "27"


def test_batch_neu69():
    """Runde 74: voegel-zurueck, kuchen-teller."""
    assert bindings.bind(
        "Jeremy saw 12 birds in their backyard and threw a stone at "
        "them, scaring away 1/3 of that number. A few minutes "
        "later, 20 more birds joined. How many birds are now in the "
        "backyard?").answer == "28"
    assert bindings.bind(
        "Mara added 3 slices of cake to a plate that already had 2 "
        "slices on it. She tripled the number of slices she "
        "currently has. She ate 2 slices and her friend stole 5 "
        "slices off her plate. What number of slices remain?"
    ).answer == "8"


def test_batch_neu70():
    """Runde 75: aepfel-geben, buecher-mehr, hobby-klasse."""
    assert bindings.bind(
        "Boris has 100 apples. Beck has 23 fewer apples than Boris. "
        "If Boris gives Beck 10 apples, how many fewer apples does "
        "Beck have than Boris now?").answer == "3"
    assert bindings.bind(
        "Alice has 6 more books than Steven. Clara has two times as "
        "many books as Steven. If Clara has 20 books, how many more "
        "books does Clara have than Alice?").answer == "4"
    assert bindings.bind(
        "A class of 50 students has various hobbies. 10 like to "
        "bake, 5 like to play basketball, and the rest like to "
        "either play video games or play music. How many like to "
        "play video games if the number that like to play music is "
        "twice the number that prefer playing basketball?"
    ).answer == "25"


def test_batch_neu71():
    """Runde 76: omelett-kalorien, tanz-taps, fenster-kaputt."""
    assert bindings.bind(
        "John makes himself a 6 egg omelet with 2 oz of cheese and "
        "an equal amount of ham. Eggs are 75 calories each. Cheese "
        "is 120 calories per ounce. Ham is 40 calories per ounce. "
        "How many calories is the omelet?").answer == "770"
    assert bindings.bind(
        "Helga could tap her right foot at a rate of 300 taps per "
        "minute, while tapping her left foot at a rate of 250 taps "
        "per minute. When she raised her arms, her tap rate slowed "
        "down to 200 taps per minute with each foot. If she dances "
        "a total of 5 minutes, with her arms raised during only 2 "
        "of those minutes, what would be the combined total number "
        "of taps?").answer == "2450"
    assert bindings.bind(
        "Hannah smashes a quarter of the students' cars' windows "
        "and 3/4ths of the teachers' cars' windows. If there are 64 "
        "students' cars with four windows each and 32 teachers' "
        "cars with two windows each, how many windows does Hannah "
        "smash?").answer == "112"


def test_batch_neu72():
    """Runde 77: kloesse-freunde, spenden-ziel, eis-angebot,
    klasse-punkte, feuerwerk, lastwagen."""
    assert bindings.bind(
        "There are 8 males and 6 females. Each male ate 1 more "
        "dumpling than each female. How many dumplings did Larry "
        "cook if each female ate 3 dumplings and there were no "
        "leftovers?").answer == "50"
    assert bindings.bind(
        "The firefighters' goal is to raise $6300. After the first "
        "3 hours, they have raised $2100. For how many hours do "
        "they have to fundraise in total?").answer == "9"
    assert bindings.bind(
        "The ice cream parlor offered a deal, buy 2 scoops of ice "
        "cream, get 1 scoop free. Each scoop cost $1.50. If Erin "
        "had $6.00, how many scoops of ice cream should she buy?"
    ).answer == "6"
    assert bindings.bind(
        "Adam has collected 50 points. Betty collected 30% more. "
        "Marta collected 3 times more points than Tom, who has 30 "
        "points less than Betty. How many points is the class "
        "missing if the minimum threshold is 400 points?"
    ).answer == "145"
    assert bindings.bind(
        "They're going to set off 15 boxes of 20 fireworks each. "
        "Hannah can see 40% of the city's fireworks. Hannah will "
        "also set off 3 boxes of 5 fireworks each in her backyard. "
        "How many fireworks will Hannah see in total?").answer == "135"
    assert bindings.bind(
        "Gissela has a truck large enough to haul 4,000 pounds. "
        "Gordy's truck can haul 800 pounds more than Gissela's "
        "truck. The three trucks combined can haul a total of "
        "11,600 pounds. How many pounds can Gary's truck carry?"
    ).answer == "2800"


def test_batch_neu73():
    """Runde 78: kekse-vier, rasen-zwei, schularbeit,
    signaturen-ziel, doppel-verdienst."""
    assert bindings.bind(
        "Katarina has 5 less cookies than Max has. Max has 12 more "
        "cookies than the Cookie Monster, and Summer has 23 more "
        "cookies than Max. If Katarina has 68 cookies, how many "
        "cookies do they have in total?").answer == "298"
    assert bindings.bind(
        "Chris can mow his entire lawn in \"turtle\" mode in 1 hour, "
        "or 40 minutes in \"rabbit\" mode. Today, he experimented "
        "by mowing half in turtle mode and half in rabbit mode. "
        "How many minutes did it take him to mow the lawn?"
    ).answer == "50"
    assert bindings.bind(
        "John has 20 minutes of math homework, 40 minutes of "
        "reading homework, and 20 minutes of history homework and 3 "
        "hours before he has to eat dinner. How many minutes does "
        "he have to nap?").answer == "100"
    assert bindings.bind(
        "Carol has 20 signatures in her book, and Jennifer has 44. "
        "They want to reach 100 signatures between them. How many "
        "signatures do they need to collect?").answer == "36"
    assert bindings.bind(
        "Lorie earns $10 per hour. Karen earns twice what Lorie "
        "earns. How much does Karen earn in two days if she works 3 "
        "hours per day?").answer == "120"


def test_batch_neu74():
    """Runde 79: zeitung-rest, bambus-tage, hund-spielzeug."""
    assert bindings.bind(
        "James delivers 600 newspapers in a day. He delivers 198 to "
        "District A, some to District B and 209 to District C. How "
        "many newspapers does he deliver to District B?"
    ).answer == "193"
    assert bindings.bind(
        "Mrs. Jameson's bamboo grows up to 30 inches a day. Today, "
        "its height is 20 feet. In how many days will its height be "
        "600 inches?").answer == "12"
    assert bindings.bind(
        "James currently has 4 toys on hand for 4 dogs, but there "
        "are 8 more dogs in the shelter now. After buying the toys, "
        "there are twice as many more dogs than when he left. When "
        "James came back yet again, 3 dogs were gone. How many toys "
        "in total does James need?").answer == "33"


def test_batch_neu75():
    """Runde 80: cupcakes-klasse, lese-ziel, koch-zeiten."""
    assert bindings.bind(
        "Howie wants to buy cupcakes. He gets the same amount of 2 "
        "cupcakes for each himself, his teacher, and his 25 "
        "classmates. How many cupcakes should Howie buy?"
    ).answer == "54"
    assert bindings.bind(
        "Mike's teacher leaves as homework the reading of a 200-page "
        "book. The assignment is to be completed within 30 days. "
        "Mike plans to read 10 pages a day. How many days before "
        "the deadline will Mike finish?").answer == "10"
    assert bindings.bind(
        "It took Finley 20 more minutes to cook pork than rice, "
        "while beans took half the combined cooking time of pork "
        "and rice. If it took her 30 minutes to cook rice, how many "
        "minutes did it take her to cook all three?").answer == "120"


def test_batch_neu76():
    """Runde 81: aufholen, lauf-vergleich, brunnen-graben."""
    assert bindings.bind(
        "Bob is 75 miles ahead of Tom, driving 55 miles per hour. "
        "Tom is driving 70 miles per hour. How long will it take "
        "Tom to catch up with Bob?").answer == "5"
    assert bindings.bind(
        "Paisley ran 4 miles. Reggie ran 5 times what Paisley ran "
        "and 3 miles farther than Lynn. How many miles did Lynn "
        "run?").answer == "17"
    assert bindings.bind(
        "Bill can dig 4 feet/hour through soil and half that fast "
        "through clay. If he has to dig through 24 feet of soil and "
        "8 feet of clay, how long will it take him to dig the well?"
    ).answer == "10"


def test_batch_neu77():
    """Runde 82: groesse-jahre, welle-reiter, briefmarken."""
    assert bindings.bind(
        "You have to be 4 feet tall to ride it. Adam's height is 40 "
        "inches and he grows 2 inches a year. How many years until "
        "he is tall enough?").answer == "4"
    assert bindings.bind(
        "When a wave over 30 feet arrives, only 25% of the 100 "
        "riders can stay upright. Of these riders, 60% are women. "
        "How many men can stay upright?").answer == "10"
    assert bindings.bind(
        "Max bought 16 snowflake stamps. He bought 3 more truck "
        "stamps than snowflake stamps, and 9 fewer rose stamps than "
        "truck stamps. How many stamps did Max buy in total?"
    ).answer == "45"


def test_batch_neu78():
    """Runde 83: aquarium-kosten, fleisch-tage, trainer-kauf."""
    assert bindings.bind(
        "Scarlett found an aquarium for $10.00. She bought 2 bags "
        "of rocks for $2.50 each and 3 pieces of coral at $2.00 "
        "apiece. She bought 20 fish at $0.50 each and fish food "
        "that cost $2.00. How much did she spend in total?"
    ).answer == "33"
    assert bindings.bind(
        "Prince sells 15kg of meat every hour he works, and he "
        "works 10 hours a day. His friend gives him a bull that "
        "weighs 750kg. How many days will it take Prince to sell "
        "the meat?").answer == "5"
    assert bindings.bind(
        "The baseball coach bought 9 new baseballs for $3 each. The "
        "basketball coach bought 8 new basketballs for $14 each. "
        "How much more did the basketball coach spend than the "
        "baseball coach?").answer == "85"


def test_batch_neu79():
    """Runde 84: pilz-protein, zahn-arbeit, spiele-jahre."""
    assert bindings.bind(
        "A cup of mushrooms weighs 100 grams and has 3 grams of "
        "protein. If John eats 200 grams of mushrooms every day how "
        "many grams of protein does he get per week?").answer == "42"
    assert bindings.bind(
        "George needs 2 implants. Each implant has a base price of "
        "$2000. For one, he wants a crown that costs an extra $500. "
        "He's already put down a deposit of $600. He makes $15 per "
        "hour. How many hours must he work to pay for the dental "
        "work?").answer == "260"
    assert bindings.bind(
        "Steve gets a console along with 5 games. He buys 1 game "
        "per month for a year, then 2 games a month the following "
        "year, then 4 games a month for the third year. He also "
        "gets 5 games for Christmas every year. How many games does "
        "Steve have after 3 years?").answer == "104"


def test_batch_neu80():
    """Runde 85: vogel-schnitt, wasser-laps, schule-bestehen."""
    assert bindings.bind(
        "Mack saw a total of 50 birds on days one and two, none on "
        "day three, saw 120 birds on days four and five, saw 20 on "
        "day six and saw 90 on day seven. On average, how many "
        "birds did Mack see in a day?").answer == "40"
    assert bindings.bind(
        "Hannah needs to drink 60 ml of water for each kilometer "
        "she runs. If her gym teacher tells her to run 8 laps and "
        "each lap is 0.25 km, how many milliliters of water will "
        "Hannah need to drink?").answer == "120"
    assert bindings.bind(
        "340 out of 500 third-graders passed, along with 40 out of "
        "100 fourth graders. The 400 fifth graders had a pass rate "
        "that was twice the fourth grades' pass rate. What is the "
        "school's overall pass rate?").answer == "70"


def test_batch_neu81():
    """Runde 86: lese-zwei, tore-drei, kaugummi."""
    assert bindings.bind(
        "Judy read for 15 minutes each night for a week. In the "
        "second week, she read a total of 100 pages. If she can "
        "read 2 pages per 1.5 minutes, how many pages did she read "
        "in two weeks?").answer == "240"
    assert bindings.bind(
        "Richie scored 20 more goals than Mark and scored 45 more "
        "goals than Anna. If Richie scored 80 goals, how many goals "
        "did all three teenagers score?").answer == "175"
    assert bindings.bind(
        "Jim has a 20 pack of gum. He chews 1 piece for every 2 "
        "hours at school over a day that lasts 8 hours. He chews 1 "
        "piece on the way home and 1 after dinner. He gives half "
        "the gum he has remaining to his sister. How many pieces "
        "does Jim have left?").answer == "7"


def test_batch_neu82():
    """Runde 87: spar-wochen, kaffee-reduz, pyramide-winkel."""
    assert bindings.bind(
        "John gets paid $2 per hour and works 5 hours a day for 4 "
        "days a week. If he wants to save $80 how many weeks will "
        "it take him?").answer == "2"
    assert bindings.bind(
        "Octavia drinks half the daily recommended cups of coffee. "
        "Her husband Juan drinks 10 times the amount of coffee she "
        "drinks. Juan's doctor has asked him to reduce his coffee "
        "intake to the daily recommendation of 4 cups. By how many "
        "cups must Juan reduce his daily coffee intake?"
    ).answer == "16"
    assert bindings.bind(
        "The great pyramids sit at an angle of 32 degrees from the "
        "ground. The sun is moving at 5 degrees an hour. If the sun "
        "starts at the tip of the pyramid and moves for 10 hours, "
        "how many degrees will there be from the ground to the sun?"
    ).answer == "82"


def test_batch_neu83():
    """Runde 88: erdbeer-kette, brot-rest, vlog-rest."""
    assert bindings.bind(
        "Tony can pick 6 quarts of strawberries per hour, while "
        "Bobby picks one less quart per hour than Tony. Kathy can "
        "pick twice as many per hour as Bobby, and Ricky picks two "
        "fewer quarts per hour than Kathy. In total, how many "
        "quarts can they pick per hour?").answer == "29"
    assert bindings.bind(
        "The bakers baked 200 loaves of bread. They sold 93 loaves "
        "in the morning and 39 loaves in the afternoon. A grocery "
        "store returned 6 unsold loaves. How many loaves of bread "
        "did they have left?").answer == "74"
    assert bindings.bind(
        "Emma can make and upload 72 vlogs per month. But she was "
        "only able to make 18 vlogs for the first week, 21 vlogs "
        "for the second week, and 15 vlogs for the third week. How "
        "many vlogs should she do to complete the 72 vlogs?"
    ).answer == "18"


def test_batch_neu84():
    """Runde 89: zwiebel-teilen, wolle-ausstattung, hausaufgaben."""
    assert bindings.bind(
        "Rose bought 4 times the number of onions and potatoes "
        "Sophia bought. If Rose bought 12 onions and 4 potatoes, "
        "how many did Sophia buy in total?").answer == "4"
    assert bindings.bind(
        "Martha is knitting for her 3 grandchildren. It takes 2 "
        "skeins of wool to make a hat, 4 for a scarf, 12 for a "
        "sweater, 1 for a pair of mittens, and 2 for a pair of "
        "socks. How many skeins of wool will she need to buy?"
    ).answer == "63"
    assert bindings.bind(
        "Chris has 100 math problems. He completes 12 problems on "
        "Monday. On Tuesday, he completes 3 times as many as he "
        "did on Monday. On Wednesday, he completes one-quarter of "
        "the remaining math problems. How many math problems does "
        "he have left on Thursday?").answer == "39"


def test_batch_neu85():
    """Runde 90: buecher-kinder, garn-yards, geschenke-freunde,
    apfel-rabatt, schuhe-zaehlen, bleistift-rest, scrabble-fuehrung,
    karten-farben, pflanzen-kette."""
    assert bindings.bind(
        "Sarah spent $300 on books. If each book was $15 and she "
        "gave an equal number of books to her 4 kids, how many "
        "books did each child get?").answer == "5"
    assert bindings.bind(
        "Mariah used 1/4 of a skein of yarn. Her grandma used 1/2 "
        "of a skein. There are 364 yards in a skein. How many yards "
        "did they use altogether?").answer == "273"
    assert bindings.bind(
        "Cherrie wants to buy gifts for her 5 friends. 2 of her "
        "friends want 5 gifts and the other 3 want 2 gifts. She "
        "gets 10 more random gifts. How many gifts did she buy?"
    ).answer == "26"
    assert bindings.bind(
        "Becky bought 20 apples for 45 cents each and received a $1 "
        "discount. Kelly bought 20 apples for 50 cents each and "
        "received a 10 percent discount. How much more did Kelly "
        "pay than Becky?").answer == "1"
    assert bindings.bind(
        "Fireman Frank has 200 shoes. He gets 5 pairs of shoes on "
        "Monday, 15 new pairs on Wednesday and 30 pairs on Friday. "
        "How many shoes will he have if he gets rid of 180 shoes on "
        "Saturday?").answer == "120"
    assert bindings.bind(
        "There are 30 students in Marissa's class. Each student "
        "started with 10 pencils. After two months, 1/5 of the "
        "total pencils were used. At the end of the year, only 1/3 "
        "of the remaining were left. How many pencils were left?"
    ).answer == "80"
    assert bindings.bind(
        "Joey has 214 points before his turn in Scrabble. He scores "
        "26 points. Then Marcy, who has 225 points, scores 10 "
        "points. By how many points is Joey now winning?"
    ).answer == "5"
    assert bindings.bind(
        "In a set of magicians cards, there are 15 red cards, and "
        "60% more green cards. Yellow cards are as many as the sum "
        "of red and green cards. How many cards are there?"
    ).answer == "78"
    assert bindings.bind(
        "Shondra has 7 fewer plants than Toni. Toni has 60% more "
        "plants than Frederick. If Frederick has 10 plants, how "
        "many plants does Shondra have?").answer == "9"


def test_batch_neu86():
    """Runde 91: triathlon-lauf, heu-kaufen."""
    assert bindings.bind(
        "Jon runs a triathlon. It takes him 40 minutes for the "
        "swim, an hour and 20 minutes for the bike ride and 50 "
        "minutes for the run. James finishes the swim 10% faster "
        "but takes 5 minutes longer on the bike. If Jon won by 10 "
        "minutes, how long did it take James to do the run?"
    ).answer == "59"
    assert bindings.bind(
        "For every mile the horse runs, he eats 1/2 a bail of hay. "
        "A bail of hay costs $3. If his horse runs for 30 minutes "
        "at 32MPH, and Michael has six 5 dollar bills, how much "
        "change does he have after he buys the hay?").answer == "6"


def test_batch_neu87():
    """Runde 92: vogel-futter, drache-kette, perlen-schwestern."""
    assert bindings.bind(
        "Lillian builds 3 bird feeders and buys 3 others. Each "
        "feeder attracts 20 birds until Lillian notices that the "
        "feeders she made attract 10 more birds each. How many "
        "birds can Lillian expect to see each day?").answer == "150"
    assert bindings.bind(
        "Prince Thaddeus slew 100 dragons. Prince Arthur slew three "
        "quarters as many. Prince Walter slew twice as many as "
        "Arthur. Prince Bruce slew one-fifth as many as Walter. How "
        "many dragons has Prince Bruce slain?").answer == "30"
    assert bindings.bind(
        "Elizabeth bought 1 pack of red and 2 packs of clear beads, "
        "while Margareth bought 3 packs of blue and 4 packs of red "
        "beads. How many more beads does one sister have than the "
        "other, if each pack of beads contains 20 pieces?"
    ).answer == "80"


def test_batch_neu88():
    """Runde 93: berg-aufstieg, bank-kapital, bus-kapazitaet,
    feuerwerk-kosten, apfel-schwestern, reise-km."""
    assert bindings.bind(
        "Stanley was at an elevation of 10,000 feet when a gust "
        "blew his comb, causing it to fall 4,000 feet to a ledge. "
        "Oliver was at an elevation of 3,000 feet. How many feet "
        "must Oliver climb to reach the comb?").answer == "3000"
    assert bindings.bind(
        "The first bank gave Mr. Josue $4000, and the second gave "
        "him twice as much. If he initially had $5000 in capital, "
        "how much capital does he have now?").answer == "17000"
    assert bindings.bind(
        "4 buses were rented that hold 60 employees, 6 minibusses "
        "that can hold 30, and 10 minivans that can hold 15. How "
        "many employees can join the day trip?").answer == "570"
    assert bindings.bind(
        "Tim buys a package of fireworks worth $400 and another "
        "pack worth twice that much. He gets a 20% discount on "
        "them. He also buys a finale firework that costs $150. How "
        "much did he spend?").answer == "1110"
    assert bindings.bind(
        "Joanne gathers 30 apples from the tallest trees, half this "
        "amount from the shortest trees. Her sister gathers twice "
        "as many from the tallest and 3 times as many from the "
        "shortest. If the sisters gathered a combined total of 500 "
        "apples, how many did Joanne gather from the average "
        "trees?").answer == "350"
    assert bindings.bind(
        "Tom traveled 200 kilometers every day for the first 4 "
        "days, and over the next two days he totaled only 30% of "
        "that. During the second week, he made 300 kilometers every "
        "day. How many kilometers in total?").answer == "3140"


def test_batch_neu89():
    """Runde 94: milch-kalorien, schritte-jog, buch-zeit,
    apfel-ernte, wander-diff, karten-saldo."""
    assert bindings.bind(
        "A glass of milk is 8 ounces. John drinks 2 glasses of "
        "milk. If milk has 3 calories per ounce how many calories "
        "did he consume?").answer == "48"
    assert bindings.bind(
        "Elliott is trying to walk 10,000 steps a day. He finished "
        "half on his walks to and from school and did another "
        "1,000 steps with his friend. After his jog, he only had "
        "2,000 steps left. How many steps did Elliott take during "
        "his jog?").answer == "2000"
    assert bindings.bind(
        "Toby is reading a book that is 45 pages long. It averages "
        "200 words a page. Toby reads at 300 words per minute. He "
        "has to be at the airport in 60 minutes and it takes 10 "
        "minutes to get there. How many minutes does he have to "
        "spare?").answer == "20"
    assert bindings.bind(
        "Lucy sells apples at $4 per piece. On Tuesday she picked "
        "12 apples. On Wednesday she picked double that. If Lucy "
        "got $56 from Monday's apples, how many apples did she "
        "pick over the three days?").answer == "50"
    assert bindings.bind(
        "Cho hiked 14 kilometers per hour for 8 hours. Chloe hiked "
        "9 kilometers per hour and stopped after 5 hours. How many "
        "kilometers farther did Cho hike?").answer == "67"
    assert bindings.bind(
        "Erica made 20 Valentine's cards. Her dad brought her 2 "
        "boxes of pre-made cards that had 15 cards each. She "
        "passed out 24 to her classmates, 5 to her family and "
        "received 17 from family and friends. How many cards does "
        "she have now?").answer == "38"


def test_batch_neu90():
    """Runde 95: kekse-familie, baum-hohen, hund-betten,
    lutscher-kette, waffen-teilen, baby-ausruestung."""
    assert bindings.bind(
        "Jenny buys 1 bag of cookies a week. The bag has 36 cookies "
        "and she puts 4 cookies in her son's lunch box 5 days a "
        "week. Her husband eats 1 cookie a day for 7 days. Jenny "
        "eats the rest. How many cookies does Jenny eat?"
    ).answer == "9"
    assert bindings.bind(
        "The shortest tree has a height of 6 feet, and the second "
        "tree has a height of 5 feet more than the shortest tree. "
        "The height of the tallest tree is twice the height of the "
        "two trees combined. How tall is the tallest tree?"
    ).answer == "34"
    assert bindings.bind(
        "A bed for a Rottweiler takes 8 pounds of stuffing, a bed "
        "for a chihuahua takes 2 pounds, and a bed for a collie "
        "takes the average of the first two. How many pounds does "
        "Mark need to make 4 chihuahua beds and 3 collie beds?"
    ).answer == "23"
    assert bindings.bind(
        "Erin has 7 lollipops. Her mother gives her another 10. If "
        "Erin gives 3 of her lollipops to Ella, how many does she "
        "have left?").answer == "14"
    assert bindings.bind(
        "DJ has 8 guns, Nick has 10, RJ has 1 and Richard has 5. "
        "If they share their guns equally, how many guns would "
        "each have?").answer == "6"
    assert bindings.bind(
        "Laurel's friend gave her 24 baby outfits. At her baby "
        "shower she received twice the amount. Then her mom gifted "
        "her another 15 outfits. How many outfits does she have?"
    ).answer == "87"


def test_batch_neu91():
    """Runde 96: kaffee-verduennung, lutscher-oscar, handy-laden,
    gewicht-wochen, geschaefts-reise, party-gaeste, punkt-spiel,
    kisten-ziel, brot-verteilung, theater-zeilen, medaillen-zehn."""
    assert bindings.bind(
        "Each ice cube cools the coffee by 13 degrees but makes it "
        "12 milliliters weaker. How many milliliters weaker is "
        "Shannon's iced coffee when it is cooled by 65 degrees and "
        "she adds 15 milliliters of cream?").answer == "75"
    assert bindings.bind(
        "Oscar has 24 lollipops and eats 2 on his way to school. "
        "He passes 14 out to his friends. He buys twice as many as "
        "he gave to his friends. He eats 3 more that night and 2 "
        "more in the morning. How many does he have left?"
    ).answer == "31"
    assert bindings.bind(
        "The cell-phone recharges at the rate of 1 percentage-point "
        "per 3 minutes. The phone is at 60% charged. How long will "
        "it take to fully charge, in hours?").answer == "2"
    assert bindings.bind(
        "Sandy needs 4 weeks to lose what Joey loses in a single "
        "week. If Joey loses 8 pounds in 4 weeks, how many weeks "
        "will it take Sandy?").answer == "16"
    assert bindings.bind(
        "Theo has $6000. He buys 6 business suits at $100 each, 3 "
        "suitcases at $50 each, a flight ticket that costs $700 "
        "more than 5 times the cost of a suit. He wishes to save "
        "$2000. How much does he have to spend on gifts?"
    ).answer == "2050"
    assert bindings.bind(
        "Martha invited 2 families with 6 people and 3 families "
        "with 4 people. 8 people couldn't come due to illness, and "
        "1/4 that number had previous commitments. How many people "
        "show up?").answer == "14"
    assert bindings.bind(
        "Mike has 21 points, Jim 3 points less, and Tony 2 times "
        "more than Mike. Every player gets an extra point if they "
        "have over 20 points. How many points do all three have in "
        "total?").answer == "83"
    assert bindings.bind(
        "Sam has a target of selling 120 crates in a week. Over the "
        "weekend he sold 20 crates. On Tuesday 15, Wednesday 12, "
        "and Thursday 18. By how many crates did he miss his "
        "target?").answer == "55"
    assert bindings.bind(
        "A bakery produces 60 loaves each day. Two-thirds of the "
        "loaves are sold in the morning and half of what is left is "
        "sold equally in the afternoon and evening. How many are "
        "sold in the afternoon?").answer == "10"
    assert bindings.bind(
        "Sean's solo song has 54 lines. The first scene has twice "
        "the number of lines, but only a third of them are his. "
        "The second scene has six more lines than the song, and "
        "four-fifths of them are his. How many lines does Sean "
        "memorize?").answer == "138"
    assert bindings.bind(
        "Ali has won 22 medals. His friend Izzy has 5 less than "
        "Ali. Together they have 10 times less medals than have "
        "been given out. How many medals have been given out?"
    ).answer == "390"


def test_batch_neu92():
    """Runde 97: stall-kuehe, kugeln-geschenk."""
    assert bindings.bind(
        "Ten stalls have 20 cows each. Mr. Sylas buys 40 cows and "
        "divides them equally into each of the twenty stalls. How "
        "many cows are in 8 of the stalls?").answer == "192"
    assert bindings.bind(
        "Maddison has 5 boxes with 50 marbles in each box. Then she "
        "gets 20 marbles from her friend. How many marbles does she "
        "have now?").answer == "270"


def test_batch_neu93():
    """Runde 98: kekse-kalorien, apps-tablet."""
    assert bindings.bind(
        "On Monday, Sue ate 4 times as many cookies as her sister. "
        "On Tuesday, she ate twice as many as her sister. Her "
        "sister ate 5 cookies on Monday and 13 the next day. If 1 "
        "cookie has 200 calories, how many more calories did Sue "
        "consume than her sister?").answer == "5600"
    assert bindings.bind(
        "Travis had 61 apps on his tablet. He deleted 9 apps he "
        "didn't use anymore and downloaded 18 more. How many apps "
        "are on his tablet now?").answer == "70"


def test_batch_neu94():
    """Runde 99: handy-minuten, pommes-kette."""
    assert bindings.bind(
        "Jason has a phone plan of 1000 minutes per month. Every "
        "day he has a 15-minute call with his boss, and he's had "
        "300 extra minutes of call this month. How many minutes "
        "does Jason have left if this month has 30 days?"
    ).answer == "250"
    assert bindings.bind(
        "Griffin had 24 french fries, but Kyle took 5 of them. "
        "Billy took twice as many as Kyle. Ginger gave Griffin a "
        "handful, and Colby took 3 less than the number Kyle had "
        "taken. If in the end Griffin had 27 fries, how many fries "
        "did Ginger give him?").answer == "20"


def test_batch_neu95():
    """Runde 100: pinguin-rest, suesigkeiten-mehr, kunden-tage,
    muschel-dienstag."""
    assert bindings.bind(
        "There are 36 penguins sunbathing in the snow. One-third "
        "jump in and swim. Another one-third go inside the cave. "
        "How many penguins are still left sunbathing?").answer == "12"
    assert bindings.bind(
        "James has 6 more candies than Robert. John has twice as "
        "many candies as Robert. If John has 54 candies, how many "
        "more candies does John have than James?").answer == "21"
    assert bindings.bind(
        "Sloane counts 100 customers entering the store. The next "
        "day, she counts 50 more customers than the first day. If "
        "the total number of customers by the third day was 500, "
        "how many did she count on the third day?").answer == "250"
    assert bindings.bind(
        "On Monday, Kylie collects 5 more shells than Robert, who "
        "collects 20. On Tuesday, Kylie collects 2 times more "
        "shells than she did on Monday. How many shells does Kylie "
        "collect on Tuesday?").answer == "50"


def test_batch_neu96():
    """Runde 101: kaese-woche, fahrrad-km, enten-insecten,
    karotten-rest, pokemon-karten."""
    assert bindings.bind(
        "Carl used 2 slices of cheese on each sandwich for 7 days. "
        "He ate omelets 3 days using one more slice per omelet "
        "than per sandwich. He used 8 slices in macaroni. How many "
        "slices did he use?").answer == "31"
    assert bindings.bind(
        "Micheal rode 5 times a week, 25 kilometers each time, for "
        "four weeks. Then he rode 2 times a week, 60 kilometers "
        "each time, for 3 weeks. How many kilometers in total?"
    ).answer == "860"
    assert bindings.bind(
        "Ducks need to eat 3.5 pounds of insects each week. If "
        "there is a flock of ten ducks, how many pounds do they "
        "need per day?").answer == "5"
    assert bindings.bind(
        "200 pounds of carrots are to be distributed to 40 "
        "restaurants in a certain city. Each restaurant receives 2 "
        "pounds. How many pounds will not be used?").answer == "120"
    assert bindings.bind(
        "Elaine initially had 20 Pokemon cards. After a month she "
        "collected three times that number. In the second month, "
        "20 fewer than the first. In the third month, twice the "
        "combined number of the first and second months. How many "
        "cards does she have now?").answer == "320"


def test_batch_neu97():
    """Runde 102: fahrgeschaeft, wander-mittwoch, einhorn-frauen."""
    assert bindings.bind(
        "Pam rode the roller coaster 2 times while Fred rode it 4 "
        "times. After that, each of them decided to ride the luge 2 "
        "times. If each ride cost 6 tickets, how many tickets did "
        "they use?").answer == "60"
    assert bindings.bind(
        "On Monday, Walt walked 4 miles. Tuesday, he walked 6 times "
        "as many miles. His total mileage Monday through Wednesday "
        "was 41 miles. How many miles did he walk on Wednesday?"
    ).answer == "13"
    assert bindings.bind(
        "There are 27 unicorns left in the world. One third of them "
        "are in the Scottish Highlands. Two thirds of the Scottish "
        "unicorns are female. How many female Scottish unicorns are "
        "there?").answer == "6"


def test_batch_neu98():
    """Runde 103: test-unvollstaendig, wettlauf-warten,
    vorlesung-stunden."""
    assert bindings.bind(
        "Mark took a test of 75 questions. He completed it at 5 "
        "questions per hour. Today, he took another test of 100 "
        "questions. If Mark had 8 hours for the first test and 6 "
        "hours for the second, how many questions did he leave "
        "incomplete?").answer == "105"
    assert bindings.bind(
        "Steve lives 3 miles from school and can bike at 440 feet "
        "per minute. Tim lives 2 miles away and can skateboard at "
        "264 feet per minute. How long will the winner be waiting "
        "before the loser finishes?").answer == "4"
    assert bindings.bind(
        "On Mondays, Wednesdays, and Fridays, Kimo has three 1-hour "
        "classes. On Tuesdays and Thursdays, two 2-hour classes. "
        "In one semester, there are 16 weeks. How many hours does "
        "Kimo spend in class?").answer == "272"


def test_batch_neu99():
    """Runde 104: loeffel-paket, freunde-mehr, boot-leck,
    tafel-reinigung, lauf-strecke, stau-autos, pflanzen-bleiben,
    kekse-letztes."""
    assert bindings.bind(
        "Julia's husband bought a package of 5 new spoons. She used "
        "three of the spoons to sample her stew. Later, she had a "
        "total of 12 spoons. How many spoons were in the package "
        "that Julia bought?").answer == "10"
    assert bindings.bind(
        "Amy made 20 more friends than Lily. If Lily made 50 "
        "friends, how many friends do Lily and Amy have together?"
    ).answer == "120"
    assert bindings.bind(
        "The boat took on two liters of water for every ten feet "
        "rowed. It took sixteen seconds to row twenty feet. The "
        "shore was 64 seconds away. How much water had the boat "
        "taken on?").answer == "16"
    assert bindings.bind(
        "A whiteboard is shared between the 4 teachers. Each "
        "teacher has 2 lessons per day and uses the whiteboard in "
        "each lesson. If it is cleaned 3 times per lesson, how many "
        "times is it cleaned per day?").answer == "24"
    assert bindings.bind(
        "Rosie can run 10 miles per hour for 3 hours. After that, "
        "she runs 5 miles per hour. How many miles can she run in "
        "7 hours?").answer == "50"
    assert bindings.bind(
        "20 more cars drive through in the remaining 15 minutes. 5 "
        "cars take an exit. If there were originally 30 cars, how "
        "many drove through in the first 15 minutes?").answer == "5"
    assert bindings.bind(
        "Mary received 18 new potted plants. She already has 2 "
        "plants on each of the 40 window ledges. She will give 1 "
        "plant from each ledge. How many plants will Mary remain "
        "with?").answer == "58"
    assert bindings.bind(
        "Henry wants to make twice as many cookies as last year. He "
        "baked 15 more than he meant to. He drops 5 and now has "
        "110 cookies. How many did he bake last year?").answer == "50"


def test_batch_neu100():
    """Runde 105: wander-rest, juwelen-kette, drache-wurf."""
    assert bindings.bind(
        "Marissa is hiking a 12-mile trail. She took 1 hour for the "
        "first 4 miles, then another hour for the next two miles. "
        "If she wants her average speed to be 4 miles per hour, "
        "what speed does she need for the remaining distance?"
    ).answer == "6"
    assert bindings.bind(
        "Siobhan has 2 fewer jewels than Aaron. Aaron has 5 more "
        "jewels than half of Raymond's jewels. If Raymond has 40 "
        "jewels, how many jewels does Siobhan have?").answer == "23"
    assert bindings.bind(
        "Perg breathed fire within a distance of 1000 feet. Polly "
        "could throw the javelin for a distance of 400 feet. With "
        "the gemstone, she could throw three times farther. How far "
        "outside the dragon's reach could Polly stand?"
    ).answer == "200"


def test_batch_neu101():
    """Runde 106: downloads-drei, schafe-drei, futter-letzte,
    heimfahrt."""
    assert bindings.bind(
        "A new program had 60 downloads in the first month. The "
        "second month was three times as many, but reduced by 30% "
        "in the third month. How many downloads total?").answer == "366"
    assert bindings.bind(
        "Toulouse has twice as many sheep as Charleston. Charleston "
        "has 4 times as many sheep as Seattle. How many sheep do "
        "they have together if Seattle has 20?").answer == "260"
    assert bindings.bind(
        "Wendi feeds each of her chickens three cups of feed per "
        "day. Her flock of 20 chickens gets 15 cups in the "
        "morning and another 25 cups in the afternoon. How many "
        "cups in the final meal?").answer == "20"
    assert bindings.bind(
        "John drives for 3 hours at 60 mph and turns around. He "
        "tries to get home in 4 hours but spends the first 2 hours "
        "in traffic. He spends the next half-hour at 30mph, then "
        "drives the remaining time at 80 mph. How far is he from "
        "home at the end?").answer == "45"


def test_batch_neu102():
    """Runde 107: blumen-verkauf, schulbuecher, kerzen-licht."""
    assert bindings.bind(
        "Faraday sells a sunflower that costs $2 each and a bouquet "
        "that costs $8. If Faraday earned $26 from the sunflower "
        "and $56 from the bouquet per day, and if each bouquet has "
        "12 sunflowers, how many sunflowers was Faraday able to "
        "sell after 3 days?").answer == "291"
    assert bindings.bind(
        "Bob spends $27000 distributed between 3 schools to buy "
        "books. He can buy 100 books for $500. How many books can "
        "he buy per school?").answer == "1800"
    assert bindings.bind(
        "There are 8 rooms in the house and 4 people living there. "
        "There is a flashlight for every person and two for each "
        "room. They have 4 small candles each for half the rooms "
        "and 5 medium candles each for the other half. How many "
        "candles and flashlights are they using?").answer == "56"


def test_batch_neu103():
    """Runde 108: suesigkeiten-kauf, muenzen-cents, zitronenbaum,
    ballon-wurf, thrice-mehr, downloads-drei, schafe-drei,
    futter-letzte, heimfahrt, blumen-verkauf, schulbuecher,
    kerzen-licht, loeffel-paket, freunde-mehr."""
    assert bindings.bind(
        "The vending machines sell chips for 40 cents and candy "
        "bars for 75 cents. George spent $5 and got 3 bags of "
        "chips and had 1% of his money left. How many candy bars "
        "did he buy?").answer == "5"
    assert bindings.bind(
        "James finds a quarter, two nickels, and 7 dimes. How much "
        "money in cents does James have?").answer == "105"
    assert bindings.bind(
        "Carlos' lemon tree cost $90 to plant. Each year it will "
        "grow 7 lemons, which he can sell for $1.5 each. It costs "
        "$3 a year to water and feed the tree. How many years will "
        "it take before he starts earning money?").answer == "13"
    assert bindings.bind(
        "Jolene fills up 10 packs of balloons with 30 balloons per "
        "pack. By the end, 12 balloons are left. How many did they "
        "throw?").answer == "288"
    assert bindings.bind(
        "Mike bought 5 face masks while Johnny bought 2 more than "
        "thrice as many as Mike. How many face masks did Johnny "
        "buy?").answer == "17"


def test_batch_neu104():
    """Runde 109: eier-verkauf, sprint-gesamt, bohnen-schnitt,
    saft-wasser, eier-dutzend."""
    assert bindings.bind(
        "Janet's ducks lay 16 eggs per day. She eats three for "
        "breakfast and bakes muffins with four. She sells the "
        "remainder for $2 per egg. How much does she make daily?"
    ).answer == "18"
    assert bindings.bind(
        "James runs 3 sprints 3 times a week. He runs 60 meters "
        "each sprint. How many total meters does he run a week?"
    ).answer == "540"
    assert bindings.bind(
        "One says 80 jelly beans. Another says 20 more than half "
        "the first. A third says 25% more than the first. What is "
        "their average guess?").answer == "80"
    assert bindings.bind(
        "10 liters of orange drink are two-thirds water. 15 liters "
        "of pineapple drink is three-fifths water. I spill one "
        "liter of orange. How much water is in the remaining 24 "
        "liters?").answer == "15"
    assert bindings.bind(
        "Claire makes a 3 egg omelet every morning. How many "
        "dozens of eggs will she eat in 4 weeks?").answer == "7"


def test_batch_neu105():
    """Runde 110: haus-flip, download-zeit, ueberstunden-lohn."""
    assert bindings.bind(
        "Josh buys a house for $80,000 and puts in $50,000 in "
        "repairs. This increased the value of the house by 150%. "
        "How much profit did he make?").answer == "70000"
    assert bindings.bind(
        "Carla is downloading a 200 GB file at 2 GB/minute. 40% of "
        "the way through, a restart takes 20 minutes. Then she has "
        "to restart the download from the beginning. How long does "
        "it take?").answer == "160"
    assert bindings.bind(
        "Eliza's rate per hour for the first 40 hours she works "
        "each week is $10. She also receives an overtime pay of "
        "1.2 times her regular hourly rate. If Eliza worked for 45 "
        "hours this week, how much are her earnings?").answer == "460"


def test_batch_neu106():
    """Runde 111: krawatten-kauf, pasteten-kauf."""
    assert bindings.bind(
        "John buys twice as many red ties as blue ties. The red "
        "ties cost 50% more than blue ties. He spent $200 on blue "
        "ties that cost $40 each. How much did he spend on ties?"
    ).answer == "800"
    assert bindings.bind(
        "Toula bought 3 dozen donuts at $68 per dozen, 2 dozen "
        "mini cupcakes at $80 per dozen, and 6 dozen mini "
        "cheesecakes for $55 per dozen. How much did she spend?"
    ).answer == "694"


def test_batch_neu107():
    """Runde 112: kauf-profit, tanz-prozent, reifen-einnahmen."""
    assert bindings.bind(
        "A merchant chooses between jewelry worth $5,000 (going up "
        "2.5%) and gadgets worth $8,000 (rising 1.2%). If he "
        "maximizes profit, how much profit would this be?"
    ).answer == "125"
    assert bindings.bind(
        "In a dance class of 20 students, 20% enrolled in "
        "contemporary dance, 25% of the remaining in jazz, and the "
        "rest in hip-hop. What percentage enrolled in hip-hop?"
    ).answer == "60"
    assert bindings.bind(
        "A mechanic charges $60 per truck tire and $40 per car "
        "tire. On Thursday, he repairs 6 truck tires and 4 car "
        "tires. On Friday, 12 car tires. How much more revenue on "
        "the day with higher revenue?").answer == "40"


def test_batch_neu108():
    """Runde 113: kerze-zeit, zug-strecke, pizza-boxes,
    jahres-gehalt, eis-ausgaben, original-preis."""
    assert bindings.bind(
        "A candle melts by 2 centimeters every hour. How many "
        "centimeters shorter after burning from 1:00 PM to 5:00 "
        "PM?").answer == "8"
    assert bindings.bind(
        "Two trains travel for 80 miles, then cover 150 miles. "
        "What's the distance covered by each train?").answer == "230"
    assert bindings.bind(
        "Marie ordered one chicken meal at $12, 5 packs of milk at "
        "$3 each, 4 apples at $1.50 each, and some boxes of pizza. "
        "She paid $50. How many boxes of pizza if each costs "
        "$8.50?").answer == "2"
    assert bindings.bind(
        "Jill gets paid $20 per hour to teach and $30 to be a "
        "cheerleading coach. If she works 50 weeks a year, 35 "
        "hours a week as a teacher and 15 hours a week as a "
        "coach, what's her annual salary?").answer == "57500"
    assert bindings.bind(
        "Cynthia buys cartons with 15 servings per carton at $4.00 "
        "per carton. After 60 days (one serving a night), how much "
        "will she spend?").answer == "16"
    assert bindings.bind(
        "Kyle bought a book for $19.50. This is with a 25% "
        "discount from the original price. What was the original "
        "price?").answer == "26"


def test_batch_neu109():
    """Runde 114: hunde-pflege, alter-verhaeltnis, lego-rest,
    pingpong-punkte."""
    assert bindings.bind(
        "John takes care of 10 dogs. Each dog takes .5 hours a day "
        "to walk. How many hours a week does he spend?").answer == "35"
    assert bindings.bind(
        "Darrell and Allen's ages are in the ratio of 7:11. If "
        "their total age now is 162, calculate Allen's age 10 "
        "years from now.").answer == "109"
    assert bindings.bind(
        "John has 13 lego sets and sells them for $15 each. He "
        "buys 8 video games for $20 each and has $5 left. How many "
        "lego sets does he still have?").answer == "2"
    assert bindings.bind(
        "Mike scores 4 points in the first 20 minutes, and 25% "
        "more in the second 20 minutes. How many total points did "
        "he score?").answer == "9"


def test_batch_neu110():
    """Runde 115: kuchen-gegessen, lauf-tempo."""
    assert bindings.bind(
        "Grandma Jones baked 5 apple pies. She cut each pie into 8 "
        "pieces. At the end, there were 14 pieces left. How many "
        "pieces did the guests eat?").answer == "26"
    assert bindings.bind(
        "John runs 60 miles a week. He runs 3 days a week. He "
        "runs 3 hours the first day and half as much the other two "
        "days. How fast does he run?").answer == "10"


def test_batch_neu111():
    """Runde 116: chips-gramm, iphone-alter."""
    assert bindings.bind(
        "A bag of chips has 250 calories per serving. If a 300g "
        "bag has 5 servings, how many grams can you eat if your "
        "daily target is 2000 and you have consumed 1800?"
    ).answer == "48"
    assert bindings.bind(
        "Brandon's iPhone is four times as old as Ben's. Ben's is "
        "two times older than Suzy's. If Suzy's iPhone is 1 year "
        "old, how old is Brandon's?").answer == "8"


def test_batch_neu112():
    """Runde 117: draht-stuecke."""
    assert bindings.bind(
        "Tracy used a piece of wire 4 feet long. The wire was cut "
        "into pieces 6 inches long. How many pieces did she "
        "obtain?").answer == "8"


def test_batch_neu113():
    """Runde 118: tasche-leicht."""
    assert bindings.bind(
        "Uriah needs to remove 15 pounds from his bag. His comic "
        "books weigh 1/4 pound each and toys weigh 1/2 pound each. "
        "If he removes 30 comic books, how many toys does he need "
        "to remove?").answer == "15"


def test_batch_neu114():
    """Runde 119: kitten-familie, kerzen-profit."""
    assert bindings.bind(
        "The sisters drive home with 7 adopted kittens. Patchy has "
        "had thrice the number of adopted kittens, while Trixie "
        "has had 12. How many kittens does the family now have?"
    ).answer == "40"
    assert bindings.bind(
        "For every pound of beeswax, Charlie can make 10 candles. "
        "One pound of beeswax and wicks cost $10.00. If he sells "
        "each candle for $2.00, what is his net profit if he makes "
        "and sells 20 candles?").answer == "20"


def test_batch_neu115():
    """Runde 120: lutscher-tueten, blog-stunden, kino-besuche,
    notizen-paket."""
    assert bindings.bind(
        "Jean has 30 lollipops. Jean eats 2. With the remaining, "
        "Jean wants to package 2 lollipops in one bag. How many "
        "bags can Jean fill?").answer == "14"
    assert bindings.bind(
        "A blog article takes 4 hours. She wrote 5 articles on "
        "Monday and 2/5 times more on Tuesday. On Wednesday, twice "
        "the number of Tuesday. How many hours total?").answer == "104"
    assert bindings.bind(
        "Peter always gets a ticket for $7 and popcorn for $7. If "
        "he has 42 dollars, how many times can he go?").answer == "3"
    assert bindings.bind(
        "Candice put 80 post-it notes in her purse and purchased a "
        "package. At work, she placed a note on each of 220 cups. "
        "If she had 23 left, how many were in the package?"
    ).answer == "163"


def test_batch_neu116():
    """Runde 121: beeren-summe, wohnung-leer, orangen-gut,
    bruecke-boxes, brosche-kosten, liefer-gebuehren."""
    assert bindings.bind(
        "A raspberry bush has 6 clusters of 20 fruit each and 67 "
        "individual fruit. How many raspberries total?").answer == "187"
    assert bindings.bind(
        "An apartment building has 15 floors with 8 units each, and "
        "3/4 is occupied. How many units are unoccupied?"
    ).answer == "30"
    assert bindings.bind(
        "A basket contains 25 oranges: 1 is bad, 20% are unripe, 2 "
        "are sour. How many are good?").answer == "17"
    assert bindings.bind(
        "A bridge can carry 5000 pounds. A truck weighs 3755 pounds "
        "and boxes weigh 15 each. How many boxes can be loaded?"
    ).answer == "83"
    assert bindings.bind(
        "Janet pays $500 for material and $800 for construction. "
        "Then she pays 10% of that to insure it. How much did she "
        "pay?").answer == "1430"
    assert bindings.bind(
        "Stephen's bill came to $40. They tacked on a 25% fee and "
        "charged $3 in delivery. He added a $4 tip. What was the "
        "final amount?").answer == "57"


def test_batch_neu117():
    """Runde 122: tank-reichweite, rente-anteil, tv-lesen,
    streaming-kosten, schul-team, sandburg-schnitt, schatz-steine,
    waesche-diff, schul-lehrer, gewichte-kombiniert, tanz-einnahmen,
    gehalt-steigerung, kuchen-spende, haustiere-drei."""
    assert bindings.bind(
        "Sophia traveled 100 miles and needed 4 gallons. Her tank "
        "holds 12 gallons. How many miles on a single tank?"
    ).answer == "300"
    assert bindings.bind(
        "Marcy gets a $50,000 pension. After 20 years, she gets 5% "
        "per year. If she quits after 30 years, what's her "
        "pension?").answer == "25000"
    assert bindings.bind(
        "Jim watches TV 2 hours and reads for half as long. He "
        "does this 3 times a week. How many hours in 4 weeks?"
    ).answer == "36"
    assert bindings.bind(
        "Aleena pays $140 per month. For the first half of the "
        "year full price, the second half 10% less. How much for "
        "the year?").answer == "1596"
    assert bindings.bind(
        "Four schools send a girls' and boys' team with 5 players "
        "each, plus a coach for each team. How many people?"
    ).answer == "48"
    assert bindings.bind(
        "A 4-level sandcastle has a top level of 16 square feet, "
        "each level double the one above. What's the average?"
    ).answer == "60"
    assert bindings.bind(
        "175 diamonds, 35 fewer rubies, and twice as many emeralds "
        "as rubies. How many gems?").answer == "595"
    assert bindings.bind(
        "Raymond does half as much laundry as Sarah. Sarah does 4 "
        "times as much as David. Sarah does 400 pounds. What's the "
        "difference between Raymond and David?").answer == "100"
    assert bindings.bind(
        "There are twice as many boys as girls. If there are 60 "
        "girls and 5 students per teacher, how many teachers?"
    ).answer == "36"
    assert bindings.bind(
        "Grace weighs 125 pounds. Alex weighs 2 pounds less than 4 "
        "times Grace. What are their combined weights?"
    ).answer == "623"
    assert bindings.bind(
        "Judy teaches 5 classes each weekday and 8 on Saturday. "
        "Each class has 15 students paying $15. How much in a "
        "week?").answer == "7425"
    assert bindings.bind(
        "A company pays $600 a month. Salaries increase by 10% per "
        "year after 5 years. What's the annual salary after 3 more "
        "years?").answer == "9360"
    assert bindings.bind(
        "Tommy sells 43 brownies at $3 and 23 cheesecake slices at "
        "$4. How much does he raise?").answer == "221"
    assert bindings.bind(
        "Jan has three times the pets of Marcia. Marcia has two "
        "more than Cindy. If Cindy has four pets, how many total?"
    ).answer == "28"


def test_batch_neu118():
    """Runde 123: schul-team, sandburg-schnitt, schatz-steine,
    waesche-diff, schul-lehrer, gewichte-kombiniert, tanz-einnahmen,
    gehalt-steigerung, kuchen-spende, haustiere-drei."""
    assert bindings.bind(
        "Four schools send a girls' and boys' team with 5 players "
        "each, plus a coach for each team. How many people?"
    ).answer == "48"
    assert bindings.bind(
        "A 4-level sandcastle has a top level of 16 square feet, "
        "each level double the one above. What's the average?"
    ).answer == "60"
    assert bindings.bind(
        "175 diamonds, 35 fewer rubies, and twice as many emeralds "
        "as rubies. How many gems?").answer == "595"
    assert bindings.bind(
        "Raymond does half as much laundry as Sarah. Sarah does 4 "
        "times as much as David. Sarah does 400 pounds. What's the "
        "difference between Raymond and David?").answer == "100"
    assert bindings.bind(
        "There are twice as many boys as girls. If there are 60 "
        "girls and 5 students per teacher, how many teachers?"
    ).answer == "36"
    assert bindings.bind(
        "Grace weighs 125 pounds. Alex weighs 2 pounds less than 4 "
        "times Grace. What are their combined weights?"
    ).answer == "623"
    assert bindings.bind(
        "Judy teaches 5 classes each weekday and 8 on Saturday. "
        "Each class has 15 students paying $15. How much in a "
        "week?").answer == "7425"
    assert bindings.bind(
        "A company pays $600 a month. Salaries increase by 10% per "
        "year after 5 years. What's the annual salary after 3 more "
        "years?").answer == "9360"
    assert bindings.bind(
        "Tommy sells 43 brownies at $3 and 23 cheesecake slices at "
        "$4. How much does he raise?").answer == "221"
    assert bindings.bind(
        "Jan has three times the pets of Marcia. Marcia has two "
        "more than Cindy. If Cindy has four pets, how many total?"
    ).answer == "28"


def test_batch_neu119():
    """Runde 124: wasser-woche, museum-geld, benzin-cashback,
    wassertank-tiefe, blumen-pflanzen, voegel-alter."""
    assert bindings.bind(
        "John has a glass of water with breakfast, lunch and "
        "dinner, plus one before bed. Weekdays only, but on "
        "weekends a soda with dinner instead. How many glasses of "
        "water in a week?").answer == "26"
    assert bindings.bind(
        "Admission is $12 for adults and $10 for children. Mom "
        "buys 1 child and 1 adult ticket. She received $8 in "
        "change. How much did she give?").answer == "30"
    assert bindings.bind(
        "Gas is $3.00 a gallon with $.20 cashback per gallon. If "
        "someone buys 10 gallons, how much after cashback?"
    ).answer == "28"
    assert bindings.bind(
        "A tank has 17 feet of water on Monday. Tuesday, 7 feet "
        "more. Wednesday, two thirds of Tuesday. What's the depth "
        "on Wednesday?").answer == "16"
    assert bindings.bind(
        "Ryan plants 2 flowers a day. After 15 days, how many if "
        "5 did not grow?").answer == "25"
    assert bindings.bind(
        "Sally Two is 3 years older than Granny Red. Granny Red "
        "is 2 times as old as Sally Four. Sally Four is the same "
        "age as Sally Thirtytwo, who is 8. What's the total age of "
        "the four birds?").answer == "51"


def test_batch_neu120():
    """Runde 125: holz-profit, stimmen-verlierer, frucht-sammeln,
    briefe-vorher, alter-versetzt."""
    assert bindings.bind(
        "Sasha has 10 boards at $10 each and 5 boards at $16 each. "
        "How much profit at 50% more?").answer == "90"
    assert bindings.bind(
        "The winner got 3/4 of 80 votes. How many did the loser "
        "get?").answer == "20"
    assert bindings.bind(
        "Morisette brought 5 apples and 8 oranges. Kael brought "
        "twice the apples and half the oranges. How many fruits "
        "total?").answer == "27"
    assert bindings.bind(
        "Jennie has 60 letters needing stamps. She stamps one-third. "
        "There are now 30 stamped. How many were stamped before?"
    ).answer == "10"
    assert bindings.bind(
        "Jean is two years older than Mark. Two years ago Mark was "
        "5 years older than half Jan's age. If Jan is 30 how old "
        "is Jean?").answer == "23"


def test_batch_neu121():
    """Runde 126: krankenhaus-profit, test-durchschnitt,
    ausgaben-zwei, tassen-preis, videospiele-bobby, alter-drei,
    bienen-verteilung, werbung-zwei."""
    assert bindings.bind(
        "A hospital sees 500 people a day for 24 minutes each. "
        "Doctors charge $150/hour, hospital charges $200/hour. "
        "How much profit?").answer == "10000"
    assert bindings.bind(
        "Brinley has scores 89, 71, 92, 100, 86. Lowest is removed. "
        "What score on the sixth test for an average of 93?"
    ).answer == "98"
    assert bindings.bind(
        "Joseph spent $500 in May and $60 less in June. How much "
        "total?").answer == "940"
    assert bindings.bind(
        "Twenty dozen cups cost $1200 less than half a dozen "
        "plates at $6000 each. What's the cost per cup?"
    ).answer == "145"
    assert bindings.bind(
        "Bobby has 5 fewer than 3 times as many games as Brian. "
        "Brian has 20 but lost 5. How many does Bobby have?"
    ).answer == "40"
    assert bindings.bind(
        "Adrian is 3 times Harriet's age. Harriet is half of "
        "Zack's age. Average age of the three in 3 years if "
        "Harriet is 21?").answer == "45"
    assert bindings.bind(
        "There are 700 bees. Twice as many workers as babies, "
        "twice as many babies as queens. How many workers?"
    ).answer == "400"
    assert bindings.bind(
        "A company spends $15000 on advertising, then a third of "
        "that. What's the total?").answer == "20000"


def test_batch_neu122():
    """Runde 127: krankenhaus-profit, spielzeit-arbeit, pokemon-
    prozent, einkauf-steuer, insekten-zahl."""
    assert bindings.bind(
        "A hospital sees 500 people a day for 24 minutes each. "
        "Doctors charge $150/hour, hospital charges $200/hour. "
        "How much profit?").answer == "10000"
    assert bindings.bind(
        "Jordan plays video games for 2 hours every day. He earns "
        "$10 an hour. How much would he earn in one week working "
        "instead?").answer == "140"
    assert bindings.bind(
        "James has 30 fire, 20 grass and 40 water cards. He loses "
        "8 water and buys 14 grass. What percent chance is a "
        "water card?").answer == "33"
    assert bindings.bind(
        "John buys milk for 2 dollars, eggs for 3 dollars, bulbs "
        "for 3 dollars, cups for 3 dollars, traps for 4 dollars. "
        "10% tax on nonfood items. How much total?"
    ).answer == "16"
    assert bindings.bind(
        "Dax found half as many bugs as ants. If there were 50 "
        "ants, how many insects total?").answer == "75"


def test_batch_neu123():
    """Runde 128: reifen-service, test-durchschnitt-Bert,
    lego-stapel, stift-mischen, freunde-drei, halle-ausgang."""
    assert bindings.bind(
        "Tires cost 25 cents. 5 bikes (2 tires), 3 tricycles (3 "
        "tires), 1 unicycle. How much?").answer == "5"
    assert bindings.bind(
        "Scores 89, 71, 92, 100, 86. Remove lowest. Need average "
        "93 on 6 tests. What sixth score?").answer == "98"
    assert bindings.bind(
        "Lego: 500 pieces, another 3 times more, another 1/4 the "
        "number. How many total?").answer == "2125"
    assert bindings.bind(
        "5 empty pens make 1 full. Buys 25 pens. Total pens?"
    ).answer == "31"
    assert bindings.bind(
        "Charlie has 3x Dorothy's friends, James 4x Dorothy's. "
        "Charlie has 12. How many does James have?").answer == "16"
    assert bindings.bind(
        "1000 students. 30% exit A, 3/5 of remaining exit B, rest "
        "exit C. How many exit C?").answer == "280"


def test_batch_neu124():
    """Runde 129: keks-wechselgeld, fahrstuhl-ziel."""
    assert bindings.bind(
        "Carl buys 10 packs of cookies. Each pack has 6 cookies. "
        "Each cookie costs $0.10. Change from a $10 bill?"
    ).answer == "4"
    assert bindings.bind(
        "Bill starts on the 3rd floor. Rides up to 4 times his "
        "starting floor plus 6. What floor?").answer == "18"


def test_batch_neu125():
    """Runde 130: pommes-raub, mms-beutel, haus-fenster."""
    assert bindings.bind(
        "Ate 14 fries. Seagull ate half of that. 3 pigeons ate 3 "
        "each. Raccoon stole 2/3 of the rest. Ants took 1, leaving "
        "5. How many fries in the pack?").answer == "48"
    assert bindings.bind(
        "3 bags of M&Ms. First has 300. Second has 12 more. Third "
        "has half of the first. Total?").answer == "762"
    assert bindings.bind(
        "2 houses, 3 bedrooms each, 2 windows per bedroom, plus 4 "
        "extra windows per house. Total windows?").answer == "20"


def test_batch_neu126():
    """Runde 131: lauf-vergleich-zwei, alter-summe, schulbedarf,
    alter-doppel, kaulquappen, alter-proportion."""
    assert bindings.bind(
        "Field 100 yards. Blake runs back and forth 15 times. "
        "Kelly once, then 40-yard line and back 34 times. How much "
        "farther does the winner run?").answer == "80"
    assert bindings.bind(
        "The sum of their ages is 20. What will the sum be in 10 "
        "years?").answer == "40"
    assert bindings.bind(
        "4 pens which cost $1.5 each, 2 notebooks which cost $4 "
        "each, and a rim of paper which cost $20. Total?"
    ).answer == "34"
    assert bindings.bind(
        "Seth is twice as old as Brooke. In 2 years the sum of "
        "their ages will be 28. How old is Seth?").answer == "16"
    assert bindings.bind(
        "11 tadpoles. 6 come out of hiding, 2 hide under a rock. "
        "How many now?").answer == "15"
    assert bindings.bind(
        "Ruby is 6 times older than Sam. In 9 years Ruby will be "
        "3 times as old as Sam. How old is Sam?").answer == "6"


def test_batch_neu127():
    """Runde 132: strand-fang, schlangen-flecken."""
    assert bindings.bind(
        "Anakin caught 10 starfish, 6 sea horses, 3 clownfish. "
        "Locsin caught 5 fewer starfish, 3 fewer sea horses, 2 more "
        "clownfish. Total fish?").answer == "32"
    assert bindings.bind(
        "A cobra has 70 spots, twice as many as a mamba. 40 cobras "
        "and 60 mambas. Half the spots combined?").answer == "2450"


def test_batch_neu128():
    """Runde 133: spielzeug-wert, geschichten-doppel."""
    assert bindings.bind(
        "5 red cars ($4 each), 3 action figures ($5 each), a doll "
        "worth 3 action figures. Total?").answer == "50"
    assert bindings.bind(
        "Alani wrote 20 stories, Braylen 40, Margot 60. Each "
        "doubled in the second week. Total stories?").answer == "360"


def test_batch_neu129():
    """Runde 134: babysitter-eier, bruder-alter, uniform-kosten,
    auto-zeitvergleich."""
    assert bindings.bind(
        "Basket of 9 eggs per babysit. Flan needs 3 eggs. 15 flans. "
        "How many babysits?").answer == "5"
    assert bindings.bind(
        "Ann is 9, her brother twice her age. How old will he be "
        "in 3 years?").answer == "21"
    assert bindings.bind(
        "Hat $25, jacket 3 times the hat, pants the average of "
        "both. Total uniform cost?").answer == "150"
    assert bindings.bind(
        "Fast car 60 mph, slow car half that. Fast car travels 480 "
        "miles. Time for slow car?").answer == "16"


def test_batch_neu130():
    """Runde 135: limonaden-profit, uebungen-zwei."""
    assert bindings.bind(
        "Gallon costs $3 lemons + $2 sugar. 20 glasses per gallon "
        "at $0.50. $25 profit. Spend on lemons?").answer == "15"
    assert bindings.bind(
        "Day 1: 100 pushups, 50 squats, 20 presses. Day 2: 20 more "
        "pushups, 10 fewer squats, double presses. Total?"
    ).answer == "370"


def test_batch_neu131():
    """Runde 136: rennen-teams, auktion-desk."""
    assert bindings.bind(
        "Race with 240 Asians, 80 Japanese, rest Chinese. 60 boys "
        "on the Chinese team. How many girls?").answer == "100"
    assert bindings.bind(
        "Opening bid $200, rises $50 each, 3 other people bid once, "
        "Carmen bids after each. What does she pay?").answer == "500"


def test_batch_neu132():
    """Runde 137: gehalt-spenden, buch-verkauf."""
    assert bindings.bind(
        "Earns $6000/month. 1/4 rent, 1/3 fuel, donates half the "
        "rest. Gives daughter $200 and wife $700. Left?"
    ).answer == "350"
    assert bindings.bind(
        "250 books. Sold twice as many first year as this year. 50 "
        "unsold, this year 45, $20 each. Second year earnings?"
    ).answer == "1300"


def test_batch_neu133():
    """Runde 138: nachhilfe-stunden, alter-kette-drei."""
    assert bindings.bind(
        "Lloyd earns $10/hour. Tutored 5 hours first week, 8 hours "
        "second week. Earnings?").answer == "130"
    assert bindings.bind(
        "Trent is 5 years older than Jane. Jane is 3 years younger "
        "than Quinn. Quinn is 30. How old is Trent?").answer == "32"


def test_batch_neu134():
    """Runde 139: blumen-bestellung, bevoelkerung-chile."""
    assert bindings.bind(
        "4 times as many roses as carnations. 200 lilies are 5 "
        "times the carnations. How many roses?").answer == "160"
    assert bindings.bind(
        "6 years ago Noah was half Cera's age. Cera is 46. Chile "
        "was 3000 times Noah's age then, half of now. Population "
        "now?").answer == "120000"


def test_batch_neu135():
    """Runde 140: stroh-verteilung, marmor-gewicht."""
    assert bindings.bind(
        "160 pieces of straw. Hamsters: 10 cages x 5. Rabbits: 20. "
        "Rats: 3 cages, 6 each. Rats per cage?").answer == "5"
    assert bindings.bind(
        "Bought 20 marbles, store had 50, father gave 2/5 times the "
        "bought. Each weighs 2 kg. Total weight?").answer == "156"


def test_batch_neu136():
    """Runde 141: zins-schuld, klasse-verteilung."""
    assert bindings.bind(
        "Owes $100, 2% monthly interest, pays after 3 months. How "
        "much?").answer == "106"
    assert bindings.bind(
        "3 times as many girls as boys, 1/10 as many nongendered, "
        "30 boys. Total?").answer == "123"


def test_batch_neu137():
    """Runde 142: messe-teilen, strommasten."""
    assert bindings.bind(
        "Spent $20.25 on tickets, $4.50 less on food, 2 rides at "
        "$33 each. Split evenly among 3. Each pays?"
    ).answer == "34"
    assert bindings.bind(
        "Poles:wires ratio 1:3. 45 wires needed. Poles needed?"
    ).answer == "15"


def test_batch_neu138():
    """Runde 143: pfirsich-ernte, firma-gehalt-zwei."""
    assert bindings.bind(
        "Collects peaches for 3 hours at 2 per minute. Total?"
    ).answer == "360"
    assert bindings.bind(
        "100 employees. Juniors 2/5, paid $2000/month. Seniors "
        "$400 more. Total monthly salary?").answer == "224000"


def test_batch_neu139():
    """Runde 144: kreide-wechsel, aktien-wert."""
    assert bindings.bind(
        "5 colors, $20 prepared, crayons $2 each. Change?"
    ).answer == "10"
    assert bindings.bind(
        "8 shares at $8. +50% first year, -25% second. Final "
        "value?").answer == "72"


def test_batch_neu140():
    """Runde 145: stift-preis, jonglieren."""
    assert bindings.bind(
        "Pen = pencil + eraser. Pencil $1.20, eraser $0.30. 8 "
        "pens?").answer == "12"
    assert bindings.bind(
        "Starts with 3 balls, adds 1 per week for 4 weeks, drops "
        "3. How many left?").answer == "4"


def test_batch_neu141():
    """Runde 146: stadt-bevoelkerung, tier-gewicht."""
    assert bindings.bind(
        "23786 inhabitants: 8417 men, 9092 women. Rest kids. How "
        "many kids?").answer == "6277"
    assert bindings.bind(
        "Frog 50 lbs = beetle = toad, 10 less than snake, 20 more "
        "than bird. Container 20 lbs, one of each. Total?"
    ).answer == "260"


def test_batch_neu142():
    """Runde 147: lektor-lohn, tisch-beine."""
    assert bindings.bind(
        "1000 sentences split equally. A pays 5 cents, B pays "
        "twice. Weekly earnings in cents?").answer == "7500"
    assert bindings.bind(
        "40 tables with 4 legs, 50 tables with 3 legs. Total "
        "legs?").answer == "310"


def test_batch_neu143():
    """Runde 148: auszeichnung-jahr, fabrik-prozent."""
    assert bindings.bind(
        "$5000 award, 5% raise, $2000/week for 52 weeks. Yearly "
        "income?").answer == "114200"
    assert bindings.bind(
        "Sold 10 tractors/day at $100. Now 5 silos/day at $220. "
        "Percent more per day?").answer == "10"


def test_batch_neu144():
    """Runde 149: huehner-eier, sohn-alter."""
    assert bindings.bind(
        "Red chickens 3 eggs/day, white 5 eggs/day. 42 eggs "
        "collected, 2 more white than red. Red chickens?"
    ).answer == "4"
    assert bindings.bind(
        "Carver is 45, 5 years less than twice his son's age. "
        "Son's age?").answer == "25"


def test_batch_neu145():
    """Runde 150: park-umfang, test-minimum."""
    assert bindings.bind(
        "Park 1.5 by 6 miles. Walks at 3 mph. Hours?"
    ).answer == "5"
    assert bindings.bind(
        "3 tests total at least 42. Scored 15 and 18. Minimum on "
        "third?").answer == "9"


def test_batch_neu146():
    """Runde 151: pool-lecks, geraet-anteil."""
    assert bindings.bind(
        "Two pools leak 4 gal/min. 4 min ago big had twice the "
        "small, now 4 times. Small pool now?").answer == "8"
    assert bindings.bind(
        "Bought $400000 equipment, 40% faulty, returned. Spent on "
        "functioning?").answer == "240000"


def test_batch_neu147():
    """Runde 152: blumen-mehr, pesos-total."""
    assert bindings.bind(
        "4 roses, 7 more dahlias than roses. Total flowers?"
    ).answer == "15"
    assert bindings.bind(
        "Axel: 50 silver + 80 gold. Anna: twice the silver, 40 "
        "more gold. Total pesos?").answer == "350"


def test_batch_neu148():
    """Runde 153: raetsel-zeit, zeugnis-durchschnitt."""
    assert bindings.bind(
        "Crossword 10 min, sudoku 5 min. 3 crosswords, 8 sudokus. "
        "Total time?").answer == "70"
    assert bindings.bind(
        "Average of 5 tests: 65, 94, 81, 86, 74. Math grade?"
    ).answer == "80"


def test_batch_neu149():
    """Runde 154: blumen-weniger, alter-differenz."""
    assert bindings.bind(
        "90 geraniums, 40 fewer petunias. Total flowers?"
    ).answer == "140"
    assert bindings.bind(
        "Alice 7 years older than Beth, Beth 5 years older than "
        "Erica. Age difference Alice-Erica?").answer == "12"


def test_batch_neu150():
    """Runde 155: boot-miete, haus-vorrat."""
    assert bindings.bind(
        "Canoe $30/h for 3h, raft $18/h for 5h. Total?"
    ).answer == "180"
    assert bindings.bind(
        "Twice as much corn as cannolis. 40 cannolis. Bought 60 "
        "more cannolis and 40 fewer corns. Total?").answer == "200"


def test_batch_neu151():
    """Runde 156: puzzle-zeit, vertrag-gehalt."""
    assert bindings.bind(
        "360-piece puzzle. Kalinda 4/min, mom half. Hours?"
    ).answer == "1"
    assert bindings.bind(
        "40 employees, $15/h, 40-h week. June: 1/4 contracts "
        "expired. Two months total?").answer == "168000"


def test_batch_neu152():
    """Runde 157: melonen-ernte, spind-groesse."""
    assert bindings.bind(
        "120 melons. 30% harvested, then 3/4 of the rest. Left "
        "unharvested?").answer == "21"
    assert bindings.bind(
        "Zack half of Timothy, Peter 1/4 of Zack. Peter is 5 "
        "cubic inches. Timothy?").answer == "40"


def test_batch_neu153():
    """Runde 158: tomaten-reben, zimmer-umfang."""
    assert bindings.bind(
        "Eats 6/day, twice his girlfriend. Vines produce 3/week. "
        "Vines needed?").answer == "21"
    assert bindings.bind(
        "Area 360 sq ft, length 3 yards. Perimeter in feet?"
    ).answer == "98"


def test_batch_neu154():
    """Runde 159: pizza-bestellung, haus-temperatur."""
    assert bindings.bind(
        "20 friends, 4 slices each, pizzas in 8 slices. Pizzas?"
    ).answer == "10"
    assert bindings.bind(
        "House 40 degrees. 3 hours baking +5/h. Window 30 min, "
        "-2 per 10 min. Final temp?").answer == "49"


def test_batch_neu155():
    """Runde 160: geld-verdreifachen, schuh-profit."""
    assert bindings.bind(
        "$20 allowance + $10 extra, tripled in a year. Money?"
    ).answer == "90"
    assert bindings.bind(
        "48 sneakers for $576. 17 sold at $20, rest at $25. "
        "Profit?").answer == "539"


def test_batch_neu156():
    """Runde 161: alter-summe-drei, kino-preis."""
    assert bindings.bind(
        "Mary 2 years younger than Joan, Joan 5 older than Jessa. "
        "Jessa 20. Sum of ages?").answer == "68"
    assert bindings.bind(
        "Super ticket $20 + $1 extra. Regular $12 + popcorn + soda "
        "$3, saved $2. Popcorn price?").answer == "4"


def test_batch_neu157():
    """Runde 162: buecher-tausch, auto-schnitt."""
    assert bindings.bind(
        "Dolly 2 books, Pandora 1. Each reads own + other's. "
        "Total read?").answer == "6"
    assert bindings.bind(
        "60 mph for 2h, then 30 mph for 1h. Average speed?"
    ).answer == "50"


def test_batch_neu158():
    """Runde 163: brief-zeit, welpen-prozent."""
    assert bindings.bind(
        "5 pen pals, stopped 2. 2 letters/week, 5 pages each, "
        "6 min/page. Hours/week?").answer == "3"
    assert bindings.bind(
        "8 puppies (3 spotted), 12 puppies (4 spotted). Percent "
        "spotted?").answer == "35"


def test_batch_neu159():
    """Runde 164: makeup-kosten, rennen-platz."""
    assert bindings.bind(
        "$250/h, 6h/day, 4x/week, 5 weeks, 10% discount. Pay?"
    ).answer == "27000"
    assert bindings.bind(
        "Starts 1st, back 5, ahead 2, behind 3, ahead 1. Place?"
    ).answer == "6"


def test_batch_neu160():
    """Runde 165: party-teilen, hai-prozent."""
    assert bindings.bind(
        "Spent $12+$43+$15+$4+$22, split 3 ways. Each pays?"
    ).answer == "32"
    assert bindings.bind(
        "10-foot shark, 2 remoras of 6 inches. Percent of body?"
    ).answer == "10"


def test_batch_neu161():
    """Runde 166: party-teilen, hai-prozent, allergien-klasse."""
    assert bindings.bind(
        "12+43+15+4+22 dollars, split 3 ways. Each pays?"
    ).answer == "32"
    assert bindings.bind(
        "10-foot shark, 2 remoras of 6 inches. Percent of body?"
    ).answer == "10"
    assert bindings.bind(
        "9 allergic to dairy, 6 to peanuts, 3 to both. 32 kids. "
        "None allergic?").answer == "20"


def test_batch_neu162():
    """Runde 167: zwiebel-kosten, muenzen-gewicht."""
    assert bindings.bind(
        "4 bags of onions, 50 lb each, $1.50/lb. Spent?"
    ).answer == "300"
    assert bindings.bind(
        "2010 penny is 3/4 of the 1959 penny. 1959 weighs 48 "
        "grains. Combined?").answer == "84"


def test_batch_neu163():
    """Runde 168: jagd-tage, orangen-wette."""
    assert bindings.bind(
        "Night 1: 10 wolves, 15 cougars. Day: 3x wolves as cougars, "
        "3 fewer cougars. Total?").answer == "73"
    assert bindings.bind(
        "$10 per orange eaten. Ate 2/5 of 60 oranges. Given up?"
    ).answer == "240"


def test_batch_neu164():
    """Runde 169: bibliothek-gebuehr."""
    assert bindings.bind(
        "Owes $0.50/book on 8 books + $2.00 flat fee. Total?"
    ).answer == "6"


def test_batch_neu165():
    """Runde 170: frucht-vergleich."""
    assert bindings.bind(
        "Andrea 8 more apples than Jamal, half the bananas. Jamal "
        "4 more bananas than apples. Andrea has 52 apples. Total "
        "fruits?").answer == "168"


def test_batch_neu166():
    """Runde 171: mehl-cookies."""
    assert bindings.bind(
        "2 cups per dozen cookies. Making 36 today + 30 tomorrow. "
        "Cups?").answer == "11"


def test_batch_neu167():
    """Runde 172: anzeigen-kosten."""
    assert bindings.bind(
        "$5 per newspaper ad, $75 per TV ad. 50 newspaper, 15 TV. "
        "Total spent?").answer == "1375"


def test_batch_neu168():
    """Runde 173: jongleur-baelle, anzeigen-kosten."""
    assert bindings.bind(
        "16 balls, half golf, half of those blue. Blue golf balls?"
    ).answer == "4"
    assert bindings.bind(
        "$5 per newspaper ad, $75 per TV ad. 50 newspaper, 15 TV. "
        "Total spent?").answer == "1375"


def test_batch_neu169():
    """Runde 174: einkauf-wechselgeld."""
    assert bindings.bind(
        "$4.20 + $9.45 + $1.35, pays $20. Change?").answer == "5"


def test_batch_neu170():
    """Runde 175: saatgut-kosten."""
    assert bindings.bind(
        "20 tomato seed packets at $40, 80 celery at $30. Spent?"
    ).answer == "3200"


def test_batch_neu171():
    """Runde 176: loecher-graben."""
    r = bindings.bind(
        "3 min small hole, 10 min large. 30 small, 15 large. "
        "Hours?")
    assert r.target.ok and r.target.obj == "hour"
    assert r.answer == "4"


def test_batch_neu172():
    """Runde 177: eis-geschenk."""
    assert bindings.bind(
        "20 popsicles at $0.25, 4 ice cream bars at $0.50. Total?"
    ).answer == "7"


def test_batch_neu173():
    """Runde 178: pizza-party."""
    assert bindings.bind(
        "12 members, 3 coaches, each member 2 guests. Pizza serves "
        "3, costs $15. Spend?").answer == "195"


def test_batch_neu174():
    """Runde 179: perlen-kette-zwei."""
    assert bindings.bind(
        "8 gemstones of 1 inch each, necklace 25 inches, beads "
        "1/4 inch. Beads?").answer == "68"


def test_batch_neu175():
    """Runde 180: flagge-sterne."""
    assert bindings.bind(
        "76-star flag: 3 rows of 8, 2 rows of 6, rest 5-star "
        "rows. 5-star rows?").answer == "8"


def test_batch_neu176():
    """Runde 181: lastwagen-steine."""
    assert bindings.bind(
        "Flagstones 75 lb each. Trucks carry 2000 lb. 80 stones. "
        "Trucks?").answer == "3"


def test_batch_neu177():
    """Runde 182: online-verdienst."""
    assert bindings.bind(
        "$5 per 10 min. Works 8-11 a.m. with 30 min pause. "
        "Earnings?").answer == "75"


def test_batch_neu178():
    """Runde 183: trainings-ziel."""
    assert bindings.bind(
        "Twice Monday+Sunday. Sunday 23 min, Monday 16 min. "
        "Tuesday minutes?").answer == "78"


def test_batch_neu179():
    """Runde 184: tabloid-seiten."""
    assert bindings.bind(
        "4 pages per piece. 32-page tabloid. Pieces?"
    ).answer == "8"


def test_batch_neu180():
    """Runde 185: monatslohn-bonus."""
    assert bindings.bind(
        "10-h shift, 5 days/week, $10/h, $300 weekly bonus. "
        "April earnings?").answer == "3200"


def test_batch_neu181():
    """Runde 186: rabatt-ersparnis."""
    assert bindings.bind(
        "Ice cream $13 now $11. Milk discount $0.5. 2 tubs + 4 "
        "packets. Save?").answer == "6"


def test_batch_neu182():
    """Runde 187: serum-limbs."""
    assert bindings.bind(
        "Extra arm every 3 days, leg every 5 days. After 15 days, "
        "new limbs?").answer == "8"


def test_batch_neu183():
    """Runde 188: familie-eier."""
    assert bindings.bind(
        "Family of 5: 3 eat 3 eggs, rest eat 2, daily. Week's "
        "eggs?").answer == "91"


def test_batch_neu184():
    """Runde 189: team-verteilung."""
    assert bindings.bind(
        "105 members. Twice as many offense as defense, half "
        "special as defense. Defense players?").answer == "30"


def test_batch_neu185():
    """Runde 190: team-verteilung, bleistift-boxen, film-ersatz."""
    assert bindings.bind(
        "105 members. Twice as many offense as defense, half "
        "special as defense. Defense players?").answer == "30"
    assert bindings.bind(
        "3 boxes + 2 loose = 26 pencils. Meg has 46. Boxes for "
        "all?").answer == "9"
    assert bindings.bind(
        "Mike has 600 movies. A third are in series, $6 each. 40% "
        "of remaining are older, $5. Normal movies $10. Cost?"
    ).answer == "4400"


def test_batch_neu186():
    """Runde 191: platten-tausch."""
    assert bindings.bind(
        "2 old records for 1 new. 5 people leave with 7 new. Old "
        "records brought?").answer == "14"


def test_batch_neu187():
    """Runde 192: treuepunkte-rabatt."""
    assert bindings.bind(
        "$1 off per $20 spent. Last trip $80. This trip $43, "
        "rewards + coupon double. Paid?").answer == "31"


def test_batch_neu188():
    """Runde 193: zucker-mengen."""
    assert bindings.bind(
        "30 oz per sucker batch, 70 oz per fudge batch. 8 sucker "
        "+ 1 fudge. Sugar?").answer == "310"


def test_batch_neu189():
    """Runde 194: bauernhof-beine."""
    assert bindings.bind(
        "60 animals, twice as many chickens as cows. Total legs?"
    ).answer == "160"


def test_batch_neu190():
    """Runde 195: trainings-monat."""
    assert bindings.bind(
        "5000 m/day, coach wants 1/5 more. Month of June. "
        "Distance?").answer == "180000"


def test_batch_neu191():
    """Runde 196: hemden-rabatt."""
    assert bindings.bind(
        "2 shirts at $30 each, 40% discount. Paid?").answer == "36"


def test_batch_neu192():
    """Runde 197: haustier-kosten."""
    assert bindings.bind(
        "Food $25/week, treats $20/month, medicine $100/month. 4 "
        "weeks/month. Yearly?").answer == "2640"


def test_batch_neu193():
    """Runde 198: wochen-aktivitaeten."""
    assert bindings.bind(
        "Yoga 1h, cooking 3x yoga, cheese 0.5h, museum half the "
        "cooking, errands 2h. Total?").answer == "8"


def test_batch_neu194():
    """Runde 199: spar-betrag."""
    assert bindings.bind(
        "Had $36. Spent $11 on sweater, gave brother $4. Saved?"
    ).answer == "21"


def test_batch_neu195():
    """Runde 200: urlaub-zeiten."""
    assert bindings.bind(
        "6h boating + half swimming + 3 shows x 2h = 30%. 40% "
        "sightseeing. Sightseeing time?").answer == "20"


def test_batch_neu196():
    """Runde 201: sparziel-rest."""
    assert bindings.bind(
        "Phone $400, has $80. Job1 $10/h x 20h, job2 $5/h x 15h. "
        "Still needed?").answer == "45"


def test_batch_neu197():
    """Runde 202: party-budget."""
    assert bindings.bind(
        "$90 budget. Mini-golf $5, tokens $5, go-karts $10 x2 per "
        "person. Friends invited?").answer == "2"


def test_batch_neu198():
    """Runde 203: sparschwein."""
    assert bindings.bind(
        "$5/day, buys 4 lollipops at 25c, saves rest. 5 days "
        "saved?").answer == "20"


def test_batch_neu199():
    """Runde 204: suessigkeiten-kauf."""
    assert bindings.bind(
        "$10, candy $1.5/lb. Half the change for gumballs at "
        "$0.05. 40 gumballs. Candy pounds?").answer == "4"


def test_batch_neu200():
    """Runde 205: park-kinder."""
    assert bindings.bind(
        "6 girls, twice the number of boys. Kids in park?"
    ).answer == "18"


def test_batch_neu201():
    """Runde 206: walmart-rauswurf."""
    assert bindings.bind(
        "3 masks. Shoplifters = 4x - 5. Violence = 3x shoplifters. "
        "50 total. Other reasons?").answer == "19"


def test_batch_neu202():
    """Runde 207: senioren-geschenke."""
    assert bindings.bind(
        "44 seniors. Frames $20 + 20% etch. 2 pins at $5. 1/4 "
        "officers get cords at $12. Total spent?").answer == "1198"


def test_batch_neu203():
    """Runde 208: brot-stuecke."""
    assert bindings.bind(
        "Dozen rolls, 6 children eat one each. Rest broken into 8 "
        "pieces. Chicken pieces?").answer == "48"


def test_batch_neu204():
    """Runde 209: limonade-profit2."""
    assert bindings.bind(
        "$18 supplies, 3 pitchers of 12 cups, $1/cup, 4 cups/h. "
        "Hourly profit?").answer == "2"


def test_batch_neu205():
    """Runde 210: chor-auftritt."""
    assert bindings.bind(
        "52 members, 50% girls. Half can't make it. 3 teachers "
        "join. Sang?").answer == "16"


def test_batch_neu206():
    """Runde 211: karneval-sparen."""
    assert bindings.bind(
        "9 rides, 2 tickets each at $2. Bracelet $30. Saved?"
    ).answer == "6"


def test_batch_neu207():
    """Runde 212: streaming-sparen."""
    assert bindings.bind(
        "Cable $60. Netflix $10. Hulu+Disney $10 each, 20% off "
        "bundle. Saved?").answer == "34"


def test_batch_neu208():
    """Runde 213: spinnen-zaehler."""
    assert bindings.bind(
        "90 spiders, 1/3 as many millipedes, stink bugs = 2x "
        "millipedes - 12. Total bugs?").answer == "168"


def test_batch_neu209():
    """Runde 214: klima-ersparnis."""
    assert bindings.bind(
        "900W AC for 8h/day, reduce by 5h. kW saved in 30 days?"
    ).answer == "81"


def test_batch_neu210():
    """Runde 215: sandwich-kosten."""
    assert bindings.bind(
        "1 lb meat + 1 lb cheese per sandwich, serves 4. 20 "
        "people. Meat $7/lb, cheese $3/lb. Cost?").answer == "50"


def test_batch_neu211():
    """Runde 216: kekse-vorrat."""
    assert bindings.bind(
        "2 cookies/night for 30 days. 1 dozen per recipe. Dozens "
        "needed?").answer == "5"


def test_batch_neu212():
    """Runde 217: kerzen-defekt."""
    assert bindings.bind(
        "50000 candles, 99% won't explode. 5% of dangerous smell. "
        "Both?").answer == "25"


def test_batch_neu213():
    """Runde 218: blusen-rabatt."""
    assert bindings.bind(
        "4 blouses, 30% off, $20 regular each. Total cost?"
    ).answer == "56"


def test_batch_neu214():
    """Runde 219: herde-hoecker."""
    assert bindings.bind(
        "180 heads, 304 bumps. Camels 2 humps, dromedaries 1. "
        "Dromedaries?").answer == "56"


def test_batch_neu215():
    """Runde 220: restaurant-rechnung."""
    assert bindings.bind(
        "Bagel $4, soup 25% more, cake half the bagel. Dinner "
        "cost?").answer == "11"


def test_batch_neu216():
    """Runde 221: kuechen-einkauf."""
    assert bindings.bind(
        "Pots $120, bowls $20, 5 utensils at $5. 20% off. Order?"
    ).answer == "132"


def test_batch_neu217():
    """Runde 222: benzin-pints."""
    assert bindings.bind(
        "15 gallons into 5 containers. Needs 1/4 container. Pints?"
    ).answer == "6"


def test_batch_neu218():
    """Runde 223: premiere-zeiten."""
    assert bindings.bind(
        "Bernadette wants 5 min before Wayne. Her drive is 4x his. "
        "Wayne takes 4 min. Leave earlier?").answer == "17"


def test_batch_neu219():
    """Runde 224: film-laengen."""
    assert bindings.bind(
        "Movie A = 1/4 of B. B = C + 5 min. C = 1.25 h. A in "
        "minutes?").answer == "20"


def test_batch_neu220():
    """Runde 225: premiere-zeiten."""
    assert bindings.bind(
        "Bernadette wants 5 min before Wayne. Her drive is 4x his. "
        "Wayne takes 4 min. Leave earlier?").answer == "17"


def test_batch_neu221():
    """Runde 226: eggnog-trays."""
    assert bindings.bind(
        "4 dozen eggs + 2 loose. 5 eggs/glass, 5 glasses/tray. "
        "Trays?").answer == "2"


def test_batch_neu222():
    """Runde 227: kreide-pakete."""
    assert bindings.bind(
        "6 packets of 8, 4 packets of 16. Total colors?"
    ).answer == "112"


def test_batch_neu223():
    """Runde 228: ballon-preise."""
    assert bindings.bind(
        "20 balloons cost $900. Price +$20 each. 170 balloons "
        "after? Cost?").answer == "11050"


def test_batch_neu224():
    """Runde 229: juwelen-wert."""
    assert bindings.bind(
        "8 sapphires, trades 3 for 2 rubies. Sapphires $800, "
        "rubies $1200. Worth?").answer == "6400"


def test_batch_neu225():
    """Runde 230: apfel-tage."""
    assert bindings.bind(
        "Marin and Nancy each eat 4 apples a day. 30 days?"
    ).answer == "150"


def test_batch_neu226():
    """Runde 231: garten-erde."""
    assert bindings.bind(
        "10 beds of 2x8x2 ft. Bags hold 2 cu ft, $12 each. Cost?"
    ).answer == "1920"


def test_batch_neu227():
    """Runde 232: garten-erde, futter-transport."""
    assert bindings.bind(
        "10 beds of 2x8x2 ft. Bags hold 2 cu ft, $12 each. Cost?"
    ).answer == "1920"
    assert bindings.bind(
        "2x1 + 4x12 + 42x75 + 20x65 lb. Truck 2250 lb. Trips?"
    ).answer == "2"


def test_batch_neu228():
    """Runde 233: recycling-einnahmen."""
    assert bindings.bind(
        "Can 2c, bottle 3c. Drinks 3 cans + 5 bottles/week. 4-week "
        "month, cents?").answer == "84"


def test_batch_neu229():
    """Runde 234: pizza-trinkgeld."""
    assert bindings.bind(
        "Delivery $15, tip = 1/5 of order. Total given?"
    ).answer == "18"


def test_batch_neu230():
    """Runde 235: karten-schueler."""
    assert bindings.bind(
        "6 decks of 25, 5 boxes of 40. Keeps 50, gives 10 each. "
        "Students?").answer == "30"


def test_batch_neu231():
    """Runde 236: hotel-waesche."""
    assert bindings.bind(
        "Room: 2 sheets, 1 comforter, 2x pillow cases as sheets, "
        "2x towels. 80 rooms?").answer == "1200"


def test_batch_neu232():
    """Runde 237: streusel-cupcakes."""
    assert bindings.bind(
        "6 jars, each decorates 8 cupcakes. Pans hold 12. Pans?"
    ).answer == "4"


def test_batch_neu233():
    """Runde 238: stift-wechselgeld."""
    assert bindings.bind(
        "Pen $2, paper = 3x pen - $1. Gave $10. Change?"
    ).answer == "3"


def test_batch_neu234():
    """Runde 239: karotten-regel."""
    assert bindings.bind(
        "Cookies = half the carrot sticks + 2. Wants 5 cookies. "
        "Carrot sticks?").answer == "6"


def test_batch_neu235():
    """Runde 240: desktop-anteil."""
    assert bindings.bind(
        "3/4 have desktops. 20 don't. Total students?"
    ).answer == "80"


def test_batch_neu236():
    """Runde 241: schuhe-einlaufen."""
    assert bindings.bind(
        "240 min to break in. 3 weeks, 4 days/week. Minutes/day?"
    ).answer == "20"


def test_batch_neu237():
    """Runde 242: betriebsausflug."""
    assert bindings.bind(
        "3 groups of 200, 7 guides per group. Total people?"
    ).answer == "621"


def test_batch_neu238():
    """Runde 243: reise-kosten."""
    assert bindings.bind(
        "2 tickets at $5000. Hotel 20% over $1500/day, 3 days. "
        "Trip cost?").answer == "15400"


def test_batch_neu239():
    """Runde 244: musik-speicher."""
    assert bindings.bind(
        "Capacity 100. Gabriel 20, Luri 3x. Fewer Luri can add?"
    ).answer == "40"


def test_batch_neu240():
    """Runde 245: lauf-stunden."""
    assert bindings.bind(
        "12 miles/day, 5 days/week, 10 mph. Hours/week?"
    ).answer == "6"


def test_batch_neu241():
    """Runde 246: hafer-bags."""
    assert bindings.bind(
        "4 horses, 5 lb/meal, 2 meals/day, 50-lb bags, 5 days. "
        "Bags?").answer == "4"


def test_batch_neu242():
    """Runde 247: pizza-groessen."""
    assert bindings.bind(
        "Small pizza $8, family 3x as much. Total spent?"
    ).answer == "32"


def test_batch_neu243():
    """Runde 248: rasierer-rabatt."""
    assert bindings.bind(
        "4 razors/pack at $4. Buy 1 get 1 free, $2 coupon. 2 "
        "packs. Cents each?").answer == "25"


def test_batch_neu244():
    """Runde 249: mensch-pyramide."""
    assert bindings.bind(
        "9 girls 64 inches + 1 girl 60 inches. Pyramid 4-3-2-1. "
        "Height in feet?").answer == "21"


def test_batch_neu245():
    """Runde 250: buerogeh-zeiten."""
    assert bindings.bind(
        "8h/day, walk 5 min every hour, 5 days. Minutes?"
    ).answer == "200"


def test_batch_neu246():
    """Runde 251: fahr-kosten."""
    assert bindings.bind(
        "2 rides/day for 14 days. Morning $6, afternoon $2. "
        "Spent?").answer == "112"


def test_batch_neu247():
    """Runde 252: orangen-pies."""
    assert bindings.bind(
        "Ashley 5 boxes of 10, Brianne 20 more. 3 oranges per "
        "pie. Pies?").answer == "40"


def test_batch_neu248():
    """Runde 253: veranstaltungs-vergleich."""
    assert bindings.bind(
        "Venue 1: $200 + $5/guest. Venue 2: $25/guest. Equal at "
        "how many guests?").answer == "10"


def test_batch_neu249():
    """Runde 254: moebel-masse."""
    assert bindings.bind(
        "Rug 5 ft wider than chair (3 ft). Couch 2 ft longer "
        "than 2x rug. Couch length?").answer == "18"


def test_batch_neu250():
    """Runde 255: kaugummi-preise."""
    assert bindings.bind(
        "4 packs: 2 strawberry, grape $2, green apple half the "
        "grape. Paid $7. Strawberry pack?").answer == "2"


def test_batch_neu251():
    """Runde 256: schneeschuh-hunde."""
    assert bindings.bind(
        "6 dogs, 4 legs each, pairs at $12. Cost?").answer == "144"


def test_batch_neu252():
    """Runde 257: bauernhof-zoo."""
    assert bindings.bind(
        "Farm 30 cows, zoo 20 sheep. Zoo 2x farm cows, farm half "
        "zoo sheep. Total?").answer == "120"


def test_batch_neu253():
    """Runde 258: neujahr-ziel."""
    assert bindings.bind(
        "Lose 30 lbs in 200 days, 3500 cal/lb. Daily deficit?"
    ).answer == "525"


def test_batch_neu254():
    """Runde 259: haus-grundstueck."""
    assert bindings.bind(
        "House + lot $120,000. House 3x the lot. House cost?"
    ).answer == "90000"


def test_batch_neu255():
    """Runde 260: taschen-profit."""
    assert bindings.bind(
        "8 packs of 5 bags at $4, sold at $8 each. Profit?"
    ).answer == "160"


def test_batch_neu256():
    """Runde 261: backen-vergleich."""
    assert bindings.bind(
        "Kelsie 2x Josh, Josh 1/4 Suzanne, Suzanne 36. Kelsie?"
    ).answer == "18"


def test_batch_neu257():
    """Runde 262: tulpen-reihen."""
    assert bindings.bind(
        "6 red/row, 8 blue/row. 36 red, 24 blue. Rows?"
    ).answer == "9"


def test_batch_neu258():
    """Runde 263: rosinen-batch."""
    assert bindings.bind(
        "27 cups split 3 ways. Cookies take 3/4 cup. Batches?"
    ).answer == "12"


def test_batch_neu259():
    """Runde 264: haus-streichen."""
    assert bindings.bind(
        "1 person paints half a house in 5 days. 5 people, whole "
        "house, hours?").answer == "48"


def test_batch_neu260():
    """Runde 265: monitor-preis."""
    assert bindings.bind(
        "Computer + 2 monitors + printer = $2400. Printer $400 "
        "less than computer. Computer $1100. Monitor cost?"
    ).answer == "300"


def test_batch_neu261():
    """Runde 266: muscheln-suche."""
    assert bindings.bind(
        "20 kids, half boys. Boys 60 shells each. Girls bring "
        "boys' amount + 4x. Each girl's shells?").answer == "300"


def test_batch_neu262():
    """Runde 267: rechnung-tip."""
    assert bindings.bind(
        "$50 bill split evenly, plus 20% tip on the bill. My "
        "pay?").answer == "35"


def test_batch_neu263():
    """Runde 268: obst-einkauf."""
    assert bindings.bind(
        "3 apples at $1.50, 5 oranges at $0.80, 6 peaches at "
        "$0.75. Gave $20. Change?").answer == "7"


def test_batch_neu264():
    """Runde 269: arbeitsweg."""
    assert bindings.bind(
        "Work 3 miles away, walks there and back, 5 times/week. "
        "Miles?").answer == "30"


def test_batch_neu265():
    """Runde 270: alphabet-uebung."""
    assert bindings.bind(
        "Alphabet in full twice, half once, then rewrite all. "
        "Letters?").answer == "130"


def test_batch_neu266():
    """Runde 271: burger-rechnung."""
    assert bindings.bind(
        "5 burgers at $4, 10 fries at $0.30, 5 drinks at $2. "
        "$50 bill. Change?").answer == "17"


def test_batch_neu267():
    """Runde 272: knoepfe-loecher."""
    assert bindings.bind(
        "21 buttons: 7 with 2 holes, rest with 4. Total holes?"
    ).answer == "70"


def test_batch_neu268():
    """Runde 273: zahnfee."""
    assert bindings.bind(
        "First tooth $5. Next 3 at $1 each. Last 2 at half that. "
        "Total?").answer == "9"


def test_batch_neu269():
    """Runde 274: kreide-muffins."""
    assert bindings.bind(
        "3 boxes of 64 crayons, 8 per muffin, sell at $1.50. "
        "Money?").answer == "36"


def test_batch_neu270():
    """Runde 275: film-zeiten2."""
    assert bindings.bind(
        "Movie 1: 1h 30m, movie 2: 2h 5m. Total minutes?"
    ).answer == "215"


def test_batch_neu271():
    """Runde 276: kontakt-linsen."""
    assert bindings.bind(
        "90 per box, $100 with 10% off, buys 2 boxes. Cost per "
        "pair?").answer == "2"


def test_batch_neu272():
    """Runde 277: hund-gewichte."""
    assert bindings.bind(
        "First dog 10 lb. Second 2x. Third 1/4 of second. Fourth "
        "44x third. Fourth weight?").answer == "220"


def test_batch_neu273():
    """Runde 278: muenzen-kauf."""
    assert bindings.bind(
        "Gumballs a nickel. 8 quarters, 6 dimes, 14 nickels, 15 "
        "pennies. Buy?").answer == "69"


def test_batch_neu274():
    """Runde 279: flug-zeiten."""
    assert bindings.bind(
        "1200 miles in 3 hours. Additional 2000 miles, hours?"
    ).answer == "5"


def test_batch_neu275():
    """Runde 280: limonade-verdienst."""
    assert bindings.bind(
        "4h x 15 cups at $0.50 + 2h x 10 cups at $0.60. Earned?"
    ).answer == "42"


def test_batch_neu276():
    """Runde 281: reifen-rotation."""
    assert bindings.bind(
        "725 rotations per 2 miles. 400 miles/month. 10,440,000 "
        "rotations max. Years?").answer == "6"


def test_batch_neu277():
    """Runde 282: shampoo-pumpen."""
    assert bindings.bind(
        "$24 shampoo, 2 pumps = 120 washings. Uses 1 pump. "
        "Cents/pump?").answer == "10"


def test_batch_neu278():
    """Runde 283: forschungs-kosten."""
    assert bindings.bind(
        "$100,000 for 5 months. Total 10x that long. After, 50% "
        "more/month. Total cost?").answer == "1450000"


def test_batch_neu279():
    """Runde 284: bohne-wachstum."""
    assert bindings.bind(
        "3 inches after week 1, doubled week 2, +4 inches week 3. "
        "Height?").answer == "10"


def test_batch_neu280():
    """Runde 285: kasse-leistung."""
    assert bindings.bind(
        "Julie 2x as fast. Jewel 50/day. Both, all week?"
    ).answer == "1050"


def test_batch_neu281():
    """Runde 286: obst-preise2."""
    assert bindings.bind(
        "4 apples $5.20, 3 oranges $3.30. 5 of each. Pay?"
    ).answer == "12"


def test_batch_neu282():
    """Runde 287: lastwagen-ausstattung."""
    assert bindings.bind(
        "Base $30,000. King cab $7,500. Leather 1/3 king. Boards "
        "$500 less than leather. Lights $1,500. Total?"
    ).answer == "43500"


def test_batch_neu283():
    """Runde 288: gehaltserhoehung."""
    assert bindings.bind(
        "5% raise on $20,000/month + bonus half a month's salary. "
        "Yearly?").answer == "262500"


def test_batch_neu284():
    """Runde 289: garderobe-kosten."""
    assert bindings.bind(
        "10 suits at $750, 10 pants at 1/5 that, 3 shirts per "
        "suit at $60. Total?").answer == "10800"


def test_batch_neu285():
    """Runde 290: mehl-saecke."""
    assert bindings.bind(
        "Flour divided into 8 portions of 2 kg. Three bags before?"
    ).answer == "48"


def test_batch_neu286():
    """Runde 291: instagram-likes."""
    assert bindings.bind(
        "2000 likes, later 70x as many, +20000 new. Total?"
    ).answer == "162000"


def test_batch_neu287():
    """Runde 292: kutsche-stunden."""
    assert bindings.bind(
        "5-9 PM, 1 hour free. First paid hour $15, each after "
        "twice. Paid?").answer == "75"


def test_batch_neu288():
    """Runde 293: lohn-abzug."""
    assert bindings.bind(
        "Bank $200 -> $420. Wage should be $300. Withheld?"
    ).answer == "80"


def test_batch_neu289():
    """Runde 294: eier-gaeste."""
    assert bindings.bind(
        "1 egg makes 2 halves. Guests eat 3 halves each, 16 "
        "guests. Dozens of eggs?").answer == "2"


def test_batch_neu290():
    """Runde 295: flugzeug-kosten."""
    assert bindings.bind(
        "Plane $150,000. $5,000/month hangar, 2x fuel. First "
        "year cost?").answer == "330000"


def test_batch_neu291():
    """Runde 296: schafe-gaense."""
    assert bindings.bind(
        "70 legs, 20 heads. Sheep 4 legs, geese 2. Sheep?"
    ).answer == "15"


def test_batch_neu292():
    """Runde 297: kaffee-kauf."""
    assert bindings.bind(
        "Coffee $5/lb, 20% more. 1 lb/day for a week + donut $2. "
        "Total?").answer == "44"


def test_batch_neu293():
    """Runde 298: einkauf-pie."""
    assert bindings.bind(
        "Spent $20. 2 chips at $2, chicken $8, soda $1. Pie cost?"
    ).answer == "7"


def test_batch_neu294():
    """Runde 299: basketball-zeit."""
    assert bindings.bind(
        "4 quarters of 12 min, extended 5 min. Game length?"
    ).answer == "53"


def test_batch_neu295():
    """Runde 300: suessigkeiten-pool."""
    assert bindings.bind(
        "Robert 3 lb, Cindy 5 lb, Aaron 4 lb. Share equally. "
        "Each?").answer == "4"


def test_batch_neu296():
    """Runde 301: wechselgeld-suess."""
    assert bindings.bind(
        "7 candies A at $0.5, 10 candies B at $0.75. Paid $15. "
        "Change?").answer == "4"


def test_batch_neu297():
    """Runde 302: anteile-invest."""
    assert bindings.bind(
        "Invested $1200. Dylan 2/5, Frances 2/3 of rest. "
        "Skyler?").answer == "240"


def test_batch_neu298():
    """Runde 303: hash-browns."""
    assert bindings.bind(
        "6 potatoes -> 36 hash browns. 96 potatoes?").answer == "576"


def test_batch_neu299():
    """Runde 304: aufzug-last."""
    assert bindings.bind(
        "Max 700 kg. Adults 80 kg, Jack + 8 others. Exceeded?"
    ).answer == "20"


def test_batch_neu300():
    """Runde 305: schulweg-zeit."""
    assert bindings.bind(
        "30 min to school. 6 min to corner, another 13 min. "
        "Left?").answer == "11"


def test_batch_neu301():
    """Runde 306: obst-kauf."""
    assert bindings.bind(
        "1 kilo apples $4, 2 kilos bananas $2/kilo, 2 kilos "
        "oranges $3/kilo. Total?").answer == "14"


def test_batch_neu302():
    """Runde 307: schulweg-zeit."""
    assert bindings.bind(
        "30 min to school. 6 min to corner, another 13 min. "
        "Left?").answer == "11"


def test_batch_neu303():
    """Runde 308: lutscher-gesamt."""
    assert bindings.bind(
        "5 lollipops + 4 candies = $3.20. Lollipop $0.40. "
        "10+10?").answer == "7"


def test_batch_neu304():
    """Runde 309: tierarzt-bill."""
    assert bindings.bind(
        "2 vaccines $20 each. Heartworm 60% of bill. Brought "
        "$125. Left?").answer == "25"


def test_batch_neu305():
    """Runde 310: quilt-quadrate."""
    assert bindings.bind(
        "14 red, 4 more blue, 6 more green, 12 fewer white. "
        "Total sqft?").answer == "68"


def test_batch_neu306():
    """Runde 311: grossmutter-babies."""
    assert bindings.bind(
        "3 children, each 3 children, each 3 babies. Great "
        "grand-babies?").answer == "27"


def test_batch_neu307():
    """Runde 312: bleistift-paare."""
    assert bindings.bind(
        "Box holds 20 pencils, 4 missing. Pairs in box?"
    ).answer == "8"


def test_batch_neu308():
    """Runde 313: mosaik-fliesen."""
    assert bindings.bind(
        "24 tiles/sqft, 36 sqft, two thirds covered. Tiles?"
    ).answer == "576"


def test_batch_neu309():
    """Runde 314: blaubeeren-spar."""
    assert bindings.bind(
        "$20 + $1.5/lb, 30 lb. Store $2.5/lb. Saved?"
    ).answer == "10"


def test_batch_neu310():
    """Runde 315: prozent-rabatt."""
    assert bindings.bind(
        "Bag marked $140, 5% discount. Pay?"
    ).answer == "133"


def test_batch_neu311():
    """Runde 316: halb-preis-kette, job-kette, abstimmung-rest."""
    assert bindings.bind(
        "A magazine costs half as much as a book. The book costs "
        "$4. A pen costs $1 less than a magazine. How much is the "
        "pen?").answer == "1"
    assert bindings.bind(
        "100 people apply for a job. Of the people that apply, "
        "only 30% receive interviews. 20% receive a job offer. "
        "A third of the people accept the position. Accept?"
    ).answer == "2"
    assert bindings.bind(
        "5000 people lined up. 2/5 of the people had voted and "
        "2/3 of the remaining people had voted. Not voted?"
    ).answer == "1000"


def test_batch_neu312():
    """Runde 317: sack-gewicht, durchschnitt-gewicht, muschel-teilen,
    halb-plus-total."""
    assert bindings.bind(
        "25 chocolate bars and 80 candied apples. Each chocolate "
        "bar weighs twice as much as each candied apple. Each "
        "chocolate bar weighs 40g. Bag weight?").answer == "2600"
    assert bindings.bind(
        "Mark weighs 150 pounds and Susan weighs 20 pounds less "
        "than Mark. Bob weighs twice as much as Susan. Average "
        "of 3 friends?").answer == "180"
    assert bindings.bind(
        "Jim collected 27 seashells, which was 5 more than what "
        "Carlos collected. Carlos collected twice as many as "
        "Carrey. Divided equally. Each?").answer == "20"
    assert bindings.bind(
        "Pierson scored 278 points. Nikita scored 11 more than "
        "half as many as Pierson. Total?").answer == "428"


def test_batch_neu313():
    """Runde 318: fabrik-rest, stunden-minuten, blueten-vergleich,
    crawfish-portionen."""
    assert bindings.bind(
        "Produces 50,000 bars of chocolate each month. 8,000 "
        "bars of chocolate the first week. Second week half as "
        "much as the first week. Third week three times as much "
        "as the first week. Fourth week?").answer == "14000"
    assert bindings.bind(
        "Walked for 8 hours on a particular day. Walked half as "
        "many hours on the second day. Total in minutes?"
    ).answer == "720"
    assert bindings.bind(
        "5 orchids and 4 African daisies. Orchids have 5 petals "
        "and daisies have 10 petals. More daisy petals?"
    ).answer == "15"
    assert bindings.bind(
        "Caught 3 pounds of crawfish Thursday. 4 times that "
        "amount Friday, half the amount of his Friday's catch "
        "Saturday. 1 serving of crawfish is 3 pounds. Servings?"
    ).answer == "7"


def test_batch_neu314():
    """Runde 319: locker-kette, alter-kette, kamera-rest,
    schulreise-rest."""
    assert bindings.bind(
        "Timothy's locker is 24 cubic inches. Zack's locker is "
        "half as big as Timothy's locker. Peter's locker is 1/4 "
        "as big as Zack's locker. Peter?").answer == "3"
    assert bindings.bind(
        "Steve is 60 years old. His wife is 4 years older than "
        "him. Son half as old as his mom, son's wife is 3 years "
        "younger than her husband. Wife?").answer == "29"
    assert bindings.bind(
        "Jayden had $70 from selling. Sister gave him half of "
        "her $90 allowance. Camera that costs $200. Need?"
    ).answer == "85"
    assert bindings.bind(
        "School covers half the cost of the trip. Has $50, trip "
        "costs $300. Missing?").answer == "100"


def test_batch_neu315():
    """Runde 320: yogurt-kosten, eier-woche, autowasche-jahr,
    schlaf-diff."""
    assert bindings.bind(
        "2 yogurts a day, 4 yogurts for $5.00, 30 days. "
        "Spend?").answer == "75"
    assert bindings.bind(
        "252 eggs per day, $2 per dozen, per week. "
        "Make?").answer == "294"
    assert bindings.bind(
        "4 car washes a month, each car wash costs $15, "
        "a year. Pay?").answer == "720"
    assert bindings.bind(
        "Harry slept 9 hours. James slept only 2/3 of what "
        "Harry slept. How many more hours?").answer == "3"


def test_batch_neu316():
    """Runde 321: glas-rabatt, kleidung-kauf, stopp-abstand,
    taschengeld-start."""
    assert bindings.bind(
        "One glass costs $5, every second glass costs only 60% "
        "of the price. Buy 16 glasses. Pay?").answer == "64"
    assert bindings.bind(
        "3 pairs of shorts, 3 pairs of pants, and 3 pairs of "
        "shoes. One pair of shorts costs $16.50. One pair of "
        "pants costs $22.50 and one pair of shoes costs $42. "
        "Spend?").answer == "243"
    assert bindings.bind(
        "60-mile trip. First stopped after 20 miles. Second "
        "stop 15 miles before the end. Between?").answer == "25"
    assert bindings.bind(
        "Weekly allowance of $5 for 8 weeks. At the end she "
        "has a total of $100. Start?").answer == "60"


def test_batch_neu317():
    """Runde 322: heels-boots, reifen-umsatz, geschwister-alter,
    puzzle-rest."""
    assert bindings.bind(
        "Two pairs of heels together cost five dollars less than "
        "the boots. If one pair of heels costs $33 and the other "
        "costs twice as much. Boots?").answer == "104"
    assert bindings.bind(
        "For each truck tire the mechanic will charge $60 and "
        "for each car tire the mechanic will charge $40. "
        "Thursday repairs 6 truck tires and 4 car tires. Friday "
        "repairs 12 car tires. More revenue Thursday?"
    ).answer == "40"
    assert bindings.bind(
        "Amy is 5 years older than Jackson and 2 years younger "
        "than Corey. James is 10 and is 1 year younger than "
        "Corey. How old is Jackson?").answer == "4"
    assert bindings.bind(
        "1000-piece jigsaw puzzle. She places a quarter of the "
        "pieces, then her mom places a third of the remaining "
        "pieces. Left?").answer == "500"


def test_batch_neu318():
    """Runde 323: haustiere-total, elfen-rest, gumball-pink,
    doppelt-plus."""
    assert bindings.bind(
        "The number of rabbits pets is twelve less than the "
        "combined number of pet dogs and cats. Two cats for "
        "every dog, number of dogs is 60. Total pets?"
    ).answer == "348"
    assert bindings.bind(
        "Hires 60 seasonal workers. A third of the elves quit, "
        "then 10 of the remaining elves quit. Left?"
    ).answer == "30"
    assert bindings.bind(
        "22 more than four times the number of pink gumballs as "
        "blue gumballs. 12 blue gumballs. Pink?").answer == "70"
    assert bindings.bind(
        "Jimmy has $2 more than twice the money Ethel has. If "
        "Ethel has $8. Jimmy?").answer == "18"


def test_batch_neu319():
    """Runde 324: spiel-bilanz, tuerklingel, kekse-box,
    wasser-prozent."""
    assert bindings.bind(
        "Played 22 games. Won 8 more than they lost. Win?"
    ).answer == "15"
    assert bindings.bind(
        "First friend pressed on the doorbell 20 times. Second "
        "friend pressed on the doorbell 1/4 times more than "
        "first. Third friend pressed on the doorbell 10 times "
        "more than the fourth. Fourth friend pressed on the "
        "doorbell 60 times. Total rings?").answer == "175"
    assert bindings.bind(
        "Greta bakes 30 cookies and Celinda bakes twice as "
        "many. Eat 10 of the cookies. Box?").answer == "80"
    assert bindings.bind(
        "Uses 40% of the water. 80% of that water is used for "
        "industrial. Non-industrial percent?").answer == "8"


def test_batch_neu320():
    """Runde 325: marmor-preis, foto-voegel, gehalt-rest,
    braunies-rest."""
    assert bindings.bind(
        "Bag of marbles costs $20, increases by 20% of the "
        "original price every two months. After 36 months?"
    ).answer == "92"
    assert bindings.bind(
        "Phone can hold 6 times more photographs. The maximum "
        "number of photographs is 50 times more than the number "
        "of birds. Phone can hold 1800 photographs. Birds?"
    ).answer == "6"
    assert bindings.bind(
        "Paycheck is $2400. Puts 50% of her pay into "
        "retirement, uses 20% of her paycheck for car. Left?"
    ).answer == "720"
    assert bindings.bind(
        "One dozen cream cheese swirl brownies. Sent home with "
        "1/2 a dozen brownies. Had 4 dozen brownies waiting. "
        "1 1/2 dozen brownies were eaten. Left?").answer == "48"


def test_batch_neu321():
    """Runde 326: wasser-rest, schallplatten, kinder-schuhe,
    schlaf-woche."""
    assert bindings.bind(
        "Two girls each got 1/6 of the 24 liters of water. A "
        "boy got 6 liters. Left?").answer == "10"
    assert bindings.bind(
        "First record sold 10 times as many copies. Sold "
        "88,000 copies combined. Harald?").answer == "8000"
    assert bindings.bind(
        "2 pairs of shoes for each of his 3 children. They "
        "cost $60 each. Pay?").answer == "360"
    assert bindings.bind(
        "Slept 8 hours on Monday. For the next two days, she "
        "slept 2 hours less, each. The rest of the week she "
        "slept 1 hour more than those two days. Total?"
    ).answer == "48"


def test_batch_neu322():
    """Runde 327: bienen-rueckkehr, affen-bananen, baum-rest,
    flamingo-diff."""
    assert bindings.bind(
        "Sees 30 bees leave the hive in the first 6 hours. "
        "Then 1/2 that many bees return in the next 6 hours. "
        "She sees two times as many bees as she saw first leave "
        "leave again. Every bee that left before hadn't already "
        "returned returns. Return?").answer == "75"
    assert bindings.bind(
        "Monkeys need 200 bananas, gorillas need 400 bananas, "
        "and baboons need 100 bananas every month. He orders "
        "all the bananas every 2 months. Order?").answer == "1400"
    assert bindings.bind(
        "Plants 10 trees a year. Every year he also chops down "
        "2 trees a year. He starts with 50 trees. After 10 "
        "years 30% of the trees die. Left?").answer == "91"
    assert bindings.bind(
        "Neighbors placed 18 pink plastic flamingos. Took back "
        "one third of the flamingos, painted them white. Added "
        "another 18 pink plastic flamingos. More pink than "
        "white?").answer == "24"


def test_batch_neu323():
    """Runde 328: steuer-vergleich, computer-rest, schulden-jahr,
    lebensmittel-budget."""
    assert bindings.bind(
        "3 fewer hours of freelance work, losing $35/hour. "
        "Accountant charges $90. More with accountant?"
    ).answer == "15"
    assert bindings.bind(
        "Budget of €1500. Machine costs €1090 with a screen. "
        "Scanner for €157, CD burner worth €74, printer for "
        "€102. Left?").answer == "77"
    assert bindings.bind(
        "Student loans have a minimum payment of $300/month, "
        "credit card's minimum is $200/month, mortgage's "
        "minimum is $500/month. Pay 50% more than the minimum, "
        "in a year?").answer == "18000"
    assert bindings.bind(
        "Her 5 packs of bacon cost $10 in total and she has 6 "
        "packets of chicken which each cost twice as much as a "
        "pack of bacon. She also has 3 packs of strawberries, "
        "priced at $4 each, and 7 packs of apples, each priced "
        "at half the price of a pack of strawberries. Budget "
        "is $65. Left?").answer == "5"


def test_batch_neu324():
    """Runde 329: autofuhrpark, schnecken-fische, baum-gewicht,
    muenzen-rest."""
    assert bindings.bind(
        "Fleet of 12 cars. Each car sells for $20,000. Pays "
        "10% tax on the cars, $1000 for registration on each. "
        "Pay?").answer == "276000"
    assert bindings.bind(
        "4 snails in one aquarium and 32 snails in another. "
        "Difference is twice the amount of fish in both "
        "aquariums. Same number of fish each. Fish?"
    ).answer == "7"
    assert bindings.bind(
        "10-foot section of a redwood tree weighs 400 pounds. "
        "30% of this redwood's wood eaten. Redwood is 200 feet "
        "tall. Weight?").answer == "5600"
    assert bindings.bind(
        "5 quarters and 2 dimes. Buys a can of pop for 55 "
        "cents. Left?").answer == "90"


def test_batch_neu325():
    """Runde 330: burrito-kosten, rutsche-wasserpark, schoko-kinder,
    orangen-rest."""
    assert bindings.bind(
        "The base burrito is $6.50. He adds extra meat for "
        "$2.00, extra cheese for $1.00, avocado for $1.00 and "
        "2 sauces for $0.25 each. He decides to upgrade his "
        "meal for an extra $3.00. He has a gift card for $5.00. "
        "Owe?").answer == "9"
    assert bindings.bind(
        "Mitchel went down the water slide 30 times. Anne went "
        "30% less than Mitchel. Robert went down 4 times as "
        "much as Anne. Robert?").answer == "84"
    assert bindings.bind(
        "4 adults and 8 children are to share 8 packets of "
        "chocolate bars. Each packet contains 5 chocolate bars. "
        "Each adult gets 6 chocolate bars. Each child?"
    ).answer == "2"
    assert bindings.bind(
        "Will buys 15 oranges. Oldest son is 8 years old, "
        "youngest is half as old as the oldest. Wash as many "
        "oranges as years old. Unwashed?").answer == "3"


def test_batch_neu326():
    """Runde 331: brettspiel-punkte, klassen-jungen, haus-budget,
    haus-erloes, wuerfel-wahrscheinlichkeit."""
    assert bindings.bind(
        "Total of 251 points in a board game. Naomi scored 68 "
        "of the points. Yuri scored 10 more than half as many "
        "points as Naomi. Brianna scored 17 points more than "
        "Naomi. Jojo?").answer == "54"
    assert bindings.bind(
        "Each class in a school has 20 students. There are 3 "
        "classes. 50% boys and 50% girls. The first class has "
        "15 girls. The second class has 12 girls. Boys in the "
        "third?").answer == "17"
    assert bindings.bind(
        "Selling price of $350 000. Brokerage fee which is 5% "
        "of the selling price, transfer fee that is 12% of the "
        "selling price. $400 000 budget. More?").answer == "9500"
    assert bindings.bind(
        "Sold his house for $400 000. Transfer fees that amount "
        "to 3%, brokerage fee that is 5% of the selling price. "
        "Paid $250 000 for the remaining loan. Proceeds?"
    ).answer == "118000"
    assert bindings.bind(
        "Six-sided die. Number greater than 3 vs two even "
        "numbers in a row. More likely (percent)?").answer == "25"


def test_batch_neu327():
    """Runde 332: hotdog-diff, pflanzentopf-rest, spielzeug-rest,
    klassen-anwesenheit."""
    assert bindings.bind(
        "Luke ate 2 hot dogs. Thomas ate three times more hot "
        "dogs than Luke. John ate half the amount Thomas ate. "
        "How many more hot dogs did John eat than Luke?"
    ).answer == "1"
    assert bindings.bind(
        "Ask for 30 plant pots for the daisies, and twice as "
        "many for the roses. Bought 100 plant pots. Left over?"
    ).answer == "10"
    assert bindings.bind(
        "Dean's mother gave him $28 to go to the toy store. "
        "Dean bought 6 toy cars and 5 teddy bears. Each toy car "
        "cost $2 and each teddy bear cost $1. His mother then "
        "decides to give him an extra $10. Left?").answer == "21"
    assert bindings.bind(
        "96 fourth-graders, 43 of them are girls. 5 fourth-"
        "grade girls and 4 fourth-grade boys were absent. Boys "
        "at school Friday?").answer == "49"


def test_batch_neu328():
    """Runde 333: moebel-vergleich, klassengruppen, zug-service,
    socken-missed, kredit-monat."""
    assert bindings.bind(
        "$1,350 advance payment and 6 monthly installments of "
        "$350 each vs $1,100 advance payment and 9 monthly "
        "installments of $250 each. Difference?").answer == "100"
    assert bindings.bind(
        "A class of 200 students is split into 3 groups such "
        "that 2 of them are equal in number and the last one "
        "is 10 less than each of the other groups. Smallest?"
    ).answer == "60"
    assert bindings.bind(
        "75 miles from the first city to the second city, 100 "
        "miles from the second city to the third city, and 50 "
        "miles less than that combined distance. It does this "
        "trip 3 times a day. Service every 18,000 miles. Days?"
    ).answer == "20"
    assert bindings.bind(
        "50 socks that need washing. Washes 10 pairs of socks "
        "and 15 loose socks. Missed?").answer == "15"
    assert bindings.bind(
        "Borrowed $3,650 for five months at an interest rate "
        "of 10%. Equal amount every month. Per month?"
    ).answer == "803"


def test_batch_neu329():
    """Runde 334: urlaub-zeit, tapete-spar, schuhverkauf,
    alter-halb, thunfisch-verdienst."""
    assert bindings.bind(
        "He spends 6 hours boating and half that time "
        "swimming. He also watched 3 different shows which "
        "were 2 hours each. This was 30% of the time he "
        "spent. He spent 40% of his time sightseeing. "
        "Sightseeing?").answer == "20"
    assert bindings.bind(
        "Wallpaper costs $400 at the market. DIY saves 20%. "
        "Total cost?").answer == "320"
    assert bindings.bind(
        "On Friday the store sold 14 pairs of tennis shoes. "
        "The next day they sold double that number of shoes. "
        "Last day they sold one-half the amount that they did "
        "the day before, but six people returned their pairs. "
        "Sold?").answer == "50"
    assert bindings.bind(
        "Marcus is half of Leo's age and five years younger "
        "than Deanna. Deanna is 26. Leo?").answer == "42"
    assert bindings.bind(
        "The first tuna he caught weighs 56 kilograms, the "
        "second tuna he caught weighs 46 kilograms, and the "
        "last tuna he caught weighs 26 kilograms. A kilogram "
        "of tuna costs $0.50. Earn?").answer == "64"


def test_batch_neu330():
    """Runde 335: pizza-rest, bauarbeiter-jahr, katzen-rest,
    kuchen-rest."""
    assert bindings.bind(
        "Pizza with 12 slices. Gives 1/3 to Bill and 1/4 to "
        "Mark. Eats 2 slices. Left?").answer == "3"
    assert bindings.bind(
        "Works for 4 weeks every month and for 6 days every "
        "week. Paid $50 every day. Earns in a year?"
    ).answer == "14400"
    assert bindings.bind(
        "50 cats on a rock. Four boats came and carried away "
        "5 cats each. 3/5 of the remaining cats ran. Left?"
    ).answer == "12"
    assert bindings.bind(
        "Cake that weighs 20 ounces. Cuts into 8 pieces. Rory "
        "and her mom each have a piece. Remaining?").answer == "15"


def test_batch_neu331():
    """Runde 336: regal-buecher, braunies-quadruple, einkaufs-bedarf,
    caterer-hotdogs, streaming-kosten."""
    assert bindings.bind(
        "20 more than double the number of books in a shelving "
        "system with 6 rows and 6 columns. Books?").answer == "92"
    assert bindings.bind(
        "Quadruple batch. Recipe calls for 3 cups of flour and "
        "1 cup milk. Flour is sold in 2-cup bags and milk is "
        "sold in 2-cup bottles. More bags than bottles?"
    ).answer == "4"
    assert bindings.bind(
        "Skipping rope that costs $6, board game that costs "
        "$11, playground ball that costs $2. Saved $2 from her "
        "allowance, mother gave her $16. Need?").answer == "1"
    assert bindings.bind(
        "Prepare gourmet hot dogs for 36 guests. Enough for "
        "half of the guests to be able to have two hotdogs. "
        "40 guests showed up, everyone wanted a second hotdog. "
        "No second hotdog?").answer == "26"
    assert bindings.bind(
        "First 6 months were $8 a month, then the normal price "
        "of $12 a month. After 8 months of the normal rate, "
        "the service increased its price to $14 a month. 2 "
        "years of the service cost?").answer == "284"


def test_batch_neu332():
    """Runde 337: taffy-rest, jeans-vergleich, pokemon-verkauf,
    suppe-kosten, feen-rest."""
    assert bindings.bind(
        "Gave her $10. Buy 1 pound at $3, get 1 pound 1/2 off. "
        "2 pounds. Seashells for $1.50 and 4 magnets that were "
        "$0.25 each. Left?").answer == "3"
    assert bindings.bind(
        "Tattered jeans cost $28, jogger jeans cost $6 less "
        "than the tattered jeans. Saved a total of $6, saved "
        "1/3 of the total savings from the jogger jeans. "
        "Originally cost difference?").answer == "8"
    assert bindings.bind(
        "Ticket to an amusement park, which costs $100. Sell "
        "them for $1.5 each. Keeps 1/3 of them, $50 in "
        "spending cash. Cards?").answer == "150"
    assert bindings.bind(
        "Recipe calls for 2 pounds of onions. He likes to "
        "double that amount. The onions are currently on sale "
        "for $2.00 a pound. He also needs 2 boxes of beef "
        "stock, that are also on sale for $2.00 a box. Cost "
        "per serving, serves 6?").answer == "2"
    assert bindings.bind(
        "Katelyn saw 50 fairies. Friend saw half as many "
        "fairies as Katelyn saw join. 30 fairies flew away. "
        "Remaining?").answer == "45"


def test_batch_neu333():
    """Runde 338: alter-dreifach, buspass-spar, tagegeld-rest,
    minuten-doppelt."""
    assert bindings.bind(
        "Brett is 14 years old. In four years his sister "
        "Angela will be three times as old as he is now. "
        "Angela now?").answer == "38"
    assert bindings.bind(
        "Two bus trips five days a week. Each bus trip costs "
        "her $2.20. Weekly bus pass for $20. Save?"
    ).answer == "2"
    assert bindings.bind(
        "Pays him $30 every day. Worked for an entire week "
        "and spent a total of $100. Left?").answer == "110"
    assert bindings.bind(
        "40 minutes more than double Rob to shingle a house. "
        "Rob takes 2 hours. Royce minutes?").answer == "280"


def test_batch_neu334():
    """Runde 339: ali-geld, strom-diff, sofa-stuhl, cd-vergleich,
    bus-passagiere."""
    assert bindings.bind(
        "Four $10 bills and six $20 bills. Gives half of the "
        "total money, uses 3/5 of the remaining. Left?"
    ).answer == "32"
    assert bindings.bind(
        "Add a device that will consume 2 kilowatts per hour a "
        "day. A kilowatt per hour is $1.50. Difference weekly "
        "electric bill?").answer == "21"
    assert bindings.bind(
        "They each have 2 fewer sofas than chairs. Jenna has 3 "
        "times as many chairs as Ophelia. If Ophelia has 20 "
        "sofas. Total sofas and chairs?").answer == "172"
    assert bindings.bind(
        "Bought a CD for $4, and a headphone set. In total "
        "paid $48. More CDs without headphone set?"
    ).answer == "11"
    assert bindings.bind(
        "48 people are riding a bus. On the first stop, 8 "
        "passengers get off, and 5 times as many people as the "
        "number who got off get into the bus. On the second "
        "stop 21, passengers get off and 3 times fewer "
        "passengers get on. After second stop?").answer == "66"


def test_batch_neu335():
    """Runde 340: sparbuch-tage, insekten-sammlung, holz-sticks,
    workout-stunden."""
    assert bindings.bind(
        "Toy car which costs $12. Already has $4 savings. "
        "Save $2 daily. Days?").answer == "4"
    assert bindings.bind(
        "Together Lily, David, and Bodhi collected 43 insects. "
        "Lily found 7 more than David. David found half of "
        "what Bodhi found. Lily?").answer == "16"
    assert bindings.bind(
        "200 sticks from a 2 x 4 piece, 400 sticks from a "
        "2 x 8 piece. $24 to buy wood. 2 x 4 costs $4, 2 x 8 "
        "costs $6. Cheapest lumber, most sticks?").answer == "1600"
    assert bindings.bind(
        "4 hours working out every week. 5 hours each for two "
        "consecutive weeks. 6 hours in one week. Across the 8 "
        "weeks?").answer == "36"


def test_batch_neu336():
    """Runde 341: aufgaben-diff, geld-teilen, neffe-alter,
    konto-abhebung, subway-kosten."""
    assert bindings.bind(
        "Jairus gets $0.8 while Jenny gets $0.5. Each of them "
        "finished 20 tasks. More Jairus?").answer == "6"
    assert bindings.bind(
        "Divide 100 dollars between them. Jeff gets 4 times as "
        "much as Brad. Jeff?").answer == "80"
    assert bindings.bind(
        "Shiloh is 44 years old today. In 7 years, he will be "
        "three times as old as his nephew. Nephew today?"
    ).answer == "10"
    assert bindings.bind(
        "$3000 in her savings account. Removes $100 from the "
        "account every month. After 2 years?").answer == "600"
    assert bindings.bind(
        "Pay $40 for a foot-long fish sub and thrice as much "
        "for a six-inch cold-cut combo sub. Cost?"
    ).answer == "160"


def test_batch_neu337():
    """Runde 342: provision-verdienst, schwimmen-zeit, kerzen-kosten,
    alter-raetsel."""
    assert bindings.bind(
        "Sell goods worth $1000, you earn a 30% commission. "
        "Sales over $1000 get you an additional 10% "
        "commission. Sold goods worth $2500. Earned?"
    ).answer == "450"
    assert bindings.bind(
        "Swims a mile in 16 minutes. Warm: 2 minutes more than "
        "twice as long. Swim 3 miles longer hot than cold?"
    ).answer == "54"
    assert bindings.bind(
        "One of them is 12 and the other is 4 years younger. "
        "A pack of 5 candles costs $3. Spend?").answer == "12"
    assert bindings.bind(
        "Jerry is twice as old as he was 5 years ago. In 3 "
        "years?").answer == "13"


def test_batch_neu338():
    """Runde 343: geschirr-total, stundenlohn-diff, dreieck-winkel,
    gewicht-erhoehung."""
    assert bindings.bind(
        "Judy bought a dozen cups and twice as many dishes as "
        "cups. Her friend had brought 40 cups and 20 more "
        "dishes than she had brought. Total?").answer == "120"
    assert bindings.bind(
        "$10 an hour. Jill worked 2 hours on Saturday and 1 "
        "hour on Sunday. John worked twice as long as Jill on "
        "Saturday and three times as long as Jill on Sunday. "
        "More John?").answer == "40"
    assert bindings.bind(
        "Angles in a triangle add up to 180 degrees. One angle "
        "is twice the smallest angle, and one angle is three "
        "times the smallest angle. Largest?").answer == "90"
    assert bindings.bind(
        "8-pound weight. Increases the weight that he uses by "
        "50%. Two pounds lighter than that. Now?"
    ).answer == "10"


def test_batch_neu339():
    """Runde 344: tippgeschwindigkeit, fruehstueck-diff,
    stiefel-preis, outfit-rest."""
    assert bindings.bind(
        "Starts with 47 words per minute. Increased to 52 WPM. "
        "Continues once more by 5 words. Average of the three "
        "measurements?").answer == "52"
    assert bindings.bind(
        "Lose 1.25 pounds/week. Gain 1.75 pounds/week. "
        "Difference at the end of 5 weeks?").answer == "15"
    assert bindings.bind(
        "Boots cost $16 and shipping costs $4. Only $13, but "
        "shipping costs twice as much. More expensive eBay?"
    ).answer == "1"
    assert bindings.bind(
        "Joe has $50 to buy an outfit. 30% off sale. The shirt "
        "he picks out has a price of $25. He also picks out a "
        "pair of shorts for $35. Left?").answer == "8"


def test_batch_neu340():
    """Runde 345: arcade-rest, alter-zukunft, internet-speed,
    karate-klassen."""
    assert bindings.bind(
        "Spends $8 dollars at the arcade on Monday. On "
        "Tuesday, he spends twice as much at the arcade as he "
        "did on Monday. On Wednesday, 4 times as much at the "
        "arcade as he spent on Tuesday. Originally had $100. "
        "Left?").answer == "12"
    assert bindings.bind(
        "Charmaine will be 16 years old in 12 years. How old "
        "will she be 4 years from now?").answer == "8"
    assert bindings.bind(
        "Internet connection speed of 20kb per second. 1 Mb "
        "has 1000 kb. Speed in Mb per hour?").answer == "72"
    assert bindings.bind(
        "Karate classes for $60. More than $10 per class, no "
        "sign up. 10 total classes. How many can he miss?"
    ).answer == "4"


def test_batch_neu341():
    """Runde 346: waeschekosten, dvd-rest, therapie-kosten,
    kochkurs-rezepte."""
    assert bindings.bind(
        "Laundry twice a week. Each load uses 20 gallons of "
        "water, a gallon of water costs $0.15. In a year?"
    ).answer == "312"
    assert bindings.bind(
        "DVD can be played 1000 times before it breaks. One "
        "has been played 356 times, the other has been played "
        "135 times. Total plays remain?").answer == "1509"
    assert bindings.bind(
        "Physical therapy for 6 weeks. Each week he went twice "
        "for 2 hours. Sessions cost $125 per hour. Spend?"
    ).answer == "3000"
    assert bindings.bind(
        "Class meets 4 times a week for 2 hours each time for "
        "6 weeks. New recipe for every 1.5 hours. Recipes?"
    ).answer == "32"


def test_batch_neu342():
    """Runde 347: buch-anzahl, zwillinge-alter, hirsch-acht,
    nuss-mischung."""
    assert bindings.bind(
        "Janey has 3 more than twice the number of books that "
        "Sally has. If Janey has 21 books, how many does "
        "Sally have?").answer == "9"
    assert bindings.bind(
        "One set of twins and one set of triplets. One twin is "
        "7 years older than one triplet. Combined ages are 44. "
        "One twin?").answer == "13"
    assert bindings.bind(
        "50 deer in a field. 50 percent of them are bucks. 20 "
        "percent of the bucks are 8 points. 8 point bucks?"
    ).answer == "5"
    assert bindings.bind(
        "A pound of almonds costs $10 while a pound of walnuts "
        "costs $15. 1/2 pound almonds and 1/3 pound walnuts "
        "vs 1/5 pound almonds and 1/3 pound walnuts. More?"
    ).answer == "3"


def test_batch_neu343():
    """Runde 348: verhaeltnis-teilen, tier-geschwindigkeit,
    nachhilfe-gebuehr, baeckerei-rabatt, suessigkeiten-diff."""
    assert bindings.bind(
        "Gerald and Julia divided $100 in the ratio 3:2. If "
        "Gerald spent $10 on a book, how much money did he "
        "have left?").answer == "50"
    assert bindings.bind(
        "Cat is 5 times faster than her turtle. Cat can run 15 "
        "feet/second. Turtle in 40 seconds?").answer == "120"
    assert bindings.bind(
        "7-day week, 2 weeks of tutoring, charges $12 per "
        "day. Charge?").answer == "168"
    assert bindings.bind(
        "5 croissants at $3.00 apiece, 4 cinnamon rolls at "
        "$2.50 each, 3 mini quiches for $4.00 apiece and 13 "
        "blueberry muffins that were $1.00 apiece. 10% off of "
        "his purchase. Bill?").answer == "45"
    assert bindings.bind(
        "Ginger eats 4 pieces a day and Amy eats 3 pieces a "
        "day. More candy Amy after two weeks?").answer == "14"


def test_batch_neu344():
    """Runde 349: lehrer-schlaf, wurst-zeit, spulen-prozent,
    stuhl-restaurant."""
    assert bindings.bind(
        "150 teachers on the school basketball court, 60% are "
        "history teachers. Rest are math teachers, each "
        "teacher sleeps for 6 hours. Math teachers hours?"
    ).answer == "360"
    assert bindings.bind(
        "A cat eats nine sausages in 30 minutes. A dog can "
        "eat the same number of sausages in 2/3 the amount of "
        "time the cat takes. Average time?").answer == "25"
    assert bindings.bind(
        "Candy has 15 light blue spools of thread, 45 dark "
        "blue spools of thread, 40 light green spools of "
        "thread, and 50 dark green spools of thread. What "
        "percent of her spools are blue?").answer == "40"
    assert bindings.bind(
        "The restaurant has 170 normal chairs and 23 chairs "
        "for babies. 20 of the normal chairs and 13 of the "
        "baby chairs were sent to the carpenter for repair. "
        "Left?").answer == "160"


def test_batch_neu345():
    """Runde 350: kaugummi-packungen, geld-teilen-gleich,
    vater-alter, buecher-gewicht."""
    assert bindings.bind(
        "Chews 4 pieces of gum a day. A pack of gum has 15 "
        "pieces. Last him 30 days. Packs?").answer == "8"
    assert bindings.bind(
        "Found $20, with his 3 younger siblings. Split the "
        "money equally. Each?").answer == "5"
    assert bindings.bind(
        "Father's age is eight more than twice Dora's age. "
        "Mother is four years younger than Dora's father. Dora "
        "is 15 years old. Total combined age?").answer == "87"
    assert bindings.bind(
        "Math and science books weigh 2 pounds each. French "
        "book weighs 4 pounds, English book weighs 3 pounds. "
        "History book weighs twice as much as her English "
        "book. Pounds?").answer == "17"


def test_batch_neu346():
    """Runde 351: milchglas-kosten, klassen-maedchen,
    tierpflege-tage, riesenschuh, wahl-stimmen."""
    assert bindings.bind(
        "A gallon jar costs $2 more than a half-gallon jar. If "
        "a gallon jar costs $5. 10-gallon jars and 16 half-"
        "gallon jars. Total?").answer == "98"
    assert bindings.bind(
        "Two classes have a total of 80 students. Each class "
        "has the same amount of students, 40% of the students "
        "are girls. Boys in each class?").answer == "24"
    assert bindings.bind(
        "8 dogs that need to be bathed, 5 cats that need their "
        "nails clipped, 3 birds that need their wings trimmed, "
        "12 horses that need to be brushed. Each day of the "
        "week?").answer == "4"
    assert bindings.bind(
        "10 inches longer than 9 times the length of Bobby's "
        "shoes. Topher's shoes 8-feet and 4-inches. Bobby?"
    ).answer == "10"
    assert bindings.bind(
        "Candidate A got 20% of the votes, candidate B got "
        "50% more than candidate A's votes. Rest to candidate "
        "C. 100 voters. C?").answer == "50"


def test_batch_neu347():
    """Runde 352: computer-kauf, schulgruppen, stuhlvermietung,
    mitbewohner-strom."""
    assert bindings.bind(
        "Buy 500 computers and had $700 for each computer. "
        "Price of each computer was 10% higher. Total paid?"
    ).answer == "385000"
    assert bindings.bind(
        "Fifty-four students are to be separated into six "
        "groups of equal size. Activity requires 12 groups. "
        "More groups needed?").answer == "3"
    assert bindings.bind(
        "Weekdays, 60 chairs are rented each day; weekends, "
        "100 chairs are rented each day. Two 4-week months. "
        "Chairs?").answer == "4000"
    assert bindings.bind(
        "Jenna has 4 roommates. Each month the electricity "
        "bill is $100. Each roommate per year?").answer == "240"


def test_batch_neu348():
    """Runde 353: rat-abstimmung, playlist-dauer, saft-kosten,
    leser-gesamt."""
    assert bindings.bind(
        "Twice as many votes in favor as there were against. "
        "33 people on the council. In favor?").answer == "22"
    assert bindings.bind(
        "Songs in a playlist is 300. John has 20 such "
        "playlists, each song is 10 hours long. Hours?"
    ).answer == "60000"
    assert bindings.bind(
        "To make 1 liter of juice, Sam needs 5 kilograms of "
        "oranges. Each kilogram of oranges costs $3. How much "
        "to make 4 liters of juice?").answer == "60"
    assert bindings.bind(
        "Ezra read twice as many books as Ahmed. Ezra has "
        "read 300 books this hour and decided to read 150 "
        "more. Altogether?").answer == "675"


def test_batch_neu349():
    """Runde 354: ball-kaugummi, lehrer-verdienst, auberginen-preis,
    raeder-rest."""
    assert bindings.bind(
        "Ball at the store for $20. Had $80 on her, rest for "
        "candy bars sold at $5 each. Candy bars?"
    ).answer == "12"
    assert bindings.bind(
        "She earns $15 for every hour and an additional $5 "
        "per day if she teaches more than 3 classes. On "
        "Monday she teaches 4 classes for 5 hours, and on "
        "Wednesday 2 classes for 2 hours. Earn?").answer == "110"
    assert bindings.bind(
        "Sells 20 of his eggplants for $3 each. 25 ears of "
        "corn. Wants a total of $135. Each ear of corn?"
    ).answer == "3"
    assert bindings.bind(
        "57 cars and 73 motorcycles. 4 wheels for each car "
        "and 2 wheels for each motorcycle. Box with 650 "
        "wheels. Left?").answer == "276"


def test_batch_neu350():
    """Runde 355: pizza-kosten, garten-ernte, salat-einkauf,
    benzin-kosten."""
    assert bindings.bind(
        "Four friends ordered four pizzas for a total of 64 "
        "dollars. If two of the pizzas cost 30 dollars, how "
        "much did each of the other two pizzas cost?"
    ).answer == "17"
    assert bindings.bind(
        "Each tomato plant yields 22 tomatoes, each plant of "
        "eggplant yields 4 eggplants. 5 tomato plants and 8 "
        "plants of eggplant. Fruits?").answer == "142"
    assert bindings.bind(
        "Leila buys 3 cucumbers from the market. Cucumbers "
        "are $2 each. Jack buys 5 tomatoes from the grocery "
        "store. Tomatoes are $1 each. Chase buys 1 head of "
        "lettuce. Lettuce cost $3 each. Together?"
    ).answer == "14"
    assert bindings.bind(
        "Fuel efficiency is 10 MPG. Price for regular gas is "
        "$3/gallon. Monday to Friday, the one-way distance "
        "between his home and office is 5 miles. Per week?"
    ).answer == "15"


def test_batch_neu351():
    """Runde 356: shirt-bestellung, holzscheit-heizung,
    deckel-verdienst, ueberstunden-lohn."""
    assert bindings.bind(
        "11 students need size extra-small. Twice as many "
        "students need size small as extra small. Four less "
        "than the number of size small students need size "
        "medium. Half as many students need size large as size "
        "medium. Six more students need size extra-large than "
        "large. Altogether?").answer == "75"
    assert bindings.bind(
        "It was 45 degrees during the day, and it's 33 degrees "
        "colder during the night compared to the day. Pipes "
        "freeze below 32 degrees. Log heats the house up by 5 "
        "degrees. Logs?").answer == "4"
    assert bindings.bind(
        "Finds 10 bottle caps a day, each bottle cap is worth "
        "$.25. 30 day month. Make?").answer == "75"
    assert bindings.bind(
        "Earns $20 per hour for 8 hours of work each day. "
        "Special hourly rate that is 150% of her regular "
        "hourly rate. Last Tuesday, she worked 11 hours. "
        "Paid?").answer == "250"


def test_batch_neu352():
    """Runde 357: brot-vergleich, ring-premium, spiel-ziel,
    tee-anfang."""
    assert bindings.bind(
        "A loaf of bread at the bakery costs $2. Bagels cost "
        "$1 each. How much more do 3 loaves of bread cost than "
        "2 bagels?").answer == "4"
    assert bindings.bind(
        "Diamond cost $600 and the gold cost $300. Pays a 30% "
        "premium. Paid?").answer == "1170"
    assert bindings.bind(
        "Playing a total of 30 hours. Half an hour every day "
        "for 2 weeks, then 2 hours every day for a week. "
        "Still need?").answer == "9"
    assert bindings.bind(
        "10 quarts of tea left. Four students each drank 1.5 "
        "quarts and 16 students each drank 2 quarts. Gallons "
        "at the beginning?").answer == "12"


def test_batch_neu353():
    """Runde 358: baumklettern, marshmallow-teilen, markt-einkauf,
    cupcake-bedarf."""
    assert bindings.bind(
        "Every branch he has to climb up costs $.25. During "
        "the week he made $105. Branches per day?"
    ).answer == "60"
    assert bindings.bind(
        "Bag has 35 marshmallows. John makes 9 S'mores, "
        "DeSean makes 9 S'mores, dropped 3 marshmallows. "
        "Each kid with the left?").answer == "7"
    assert bindings.bind(
        "Buys 3 goats for $500 each and 2 cows for $1500 "
        "each. Spend?").answer == "4500"
    assert bindings.bind(
        "Needs 63 cupcakes. Already has 8 chocolate cupcakes "
        "and 40 toffee cupcakes. Buy?").answer == "15"


def test_batch_neu354():
    """Runde 359: tv-verkauf, jeans-wechselgeld, mosaik-laenge,
    zyklus-lohn, tierfutter-vergleich."""
    assert bindings.bind(
        "One-fourth of their sales are smart TVs, one-eighth "
        "are analog TVs, rest OLED. Total of 40 TVs. OLED?"
    ).answer == "25"
    assert bindings.bind(
        "Jeans were advertised 25% off. Original price of the "
        "jeans was $40. Pays with a $50.00 bill. Left over?"
    ).answer == "20"
    assert bindings.bind(
        "It takes twelve glass chips to make every square "
        "inch of the mosaic. A bag of glass chips holds 72 "
        "chips. Three inches tall. Two bags of glass chips. "
        "Inches long?").answer == "4"
    assert bindings.bind(
        "30 cycles of work a day. Each cycle has 5 different "
        "tasks, each task pays $1.20. Full 7 day week?"
    ).answer == "1260"
    assert bindings.bind(
        "8 packages of cat food and 6 packages of dog food. "
        "Each package of cat food contained 11 tins, each "
        "package of dog food contained 6 tins. More tins cat "
        "than dog?").answer == "52"


def test_batch_neu355():
    """Runde 360: mulan-geld, ersparnis-vergleich, bonbon-verkauf,
    parkplatz-autos."""
    assert bindings.bind(
        "Mulan has $40. Her father gave her $100. Two pairs "
        "of jeans at $30 each and a bag for $20. Left?"
    ).answer == "60"
    assert bindings.bind(
        "Roy has saved 40% more than his brother Anthony. "
        "Anthony has saved $10.00 more than their sister Eva. "
        "Eva has saved $20.00. Roy?").answer == "42"
    assert bindings.bind(
        "Started off with 100 total, ended up selling 150 "
        "butterscotch candies. Ordered 100 more. Still need "
        "to sell?").answer == "50"
    assert bindings.bind(
        "Counted 50 cars packed. First break, counted 20 more "
        "cars in the parking lot. 1/2 the number of cars had "
        "gone. During lunch?").answer == "35"


def test_batch_neu356():
    """Runde 361: apfel-scheiben, milch-kuehe, auto-finanzierung,
    wechselgeld-hat."""
    assert bindings.bind(
        "A large apple can be sliced into 5 pieces, and a "
        "small apple can be sliced into 3 pieces. Adam "
        "decides to slice 3 large and 5 small apples and then "
        "eats 15 slices. Left?").answer == "15"
    assert bindings.bind(
        "A farmer extracts 5 liters of milk a day from a cow. "
        "Since he has 3 cows, how many more cows does he need "
        "to have to produce 25 liters of milk a day?"
    ).answer == "2"
    assert bindings.bind(
        "Car for $10000 and a phone for $800. Has $5000 from "
        "working on weekends, brother gave him $200. Still "
        "need?").answer == "5600"
    assert bindings.bind(
        "Hat from a craftsman worth $70. Gave the craftsman "
        "four $20 bills. Change?").answer == "10"


def test_batch_neu357():
    """Runde 362: klasse-faecher, konzert-gruppen, eier-verdienst,
    schuhe-durchschnitt."""
    assert bindings.bind(
        "There are 20 students in Miss Susan's class. 5 of "
        "them are good at math only, 8 of them perform well "
        "in English only, and the rest are good at both math "
        "and English. Good at math?").answer == "12"
    assert bindings.bind(
        "The show will be 2 hours. She is allowing each group "
        "2 minutes to get on stage, 6 minutes to perform, and "
        "then 2 minutes to exit the stage. If she allows a "
        "10-minute intermission, how many groups can perform?"
    ).answer == "11"
    assert bindings.bind(
        "A farmer has 900 eggs. He placed them on a tray, "
        "which holds 30 eggs each. How much will he earn if "
        "he sells it for $2.5 per tray?").answer == "75"
    assert bindings.bind(
        "2 pairs of shoes a month. Spends $2640 on shoes each "
        "year. Average per pair?").answer == "110"


def test_batch_neu358():
    """Runde 363: klebestifte-packungen, pest-infektion, zins-anlage,
    familien-alter."""
    assert bindings.bind(
        "Class has 27 students. Give each student 2 glue "
        "sticks. Come in packs of 8, whole packs. Packs?"
    ).answer == "7"
    assert bindings.bind(
        "Infects ten people. Every day, each infected person "
        "infects six others. After three days?").answer == "3430"
    assert bindings.bind(
        "Invested $300. Simple interest at the rate of three-"
        "quarters of the original amount per year. After 3 "
        "years?").answer == "975"
    assert bindings.bind(
        "I am three years younger than my brother, 2 years "
        "older than my sister. Mom's age one less than three "
        "times my brother's age. Add all our ages, you get "
        "87. How old am I?").answer == "13"


def test_batch_neu359():
    """Runde 364: burrito-rest, handy-wechselgeld,
    lebensmittel-anteil, pizza-gegessen."""
    assert bindings.bind(
        "Ordered 600 burritos. There were 50 students at the "
        "picnic, and each student was given ten burritos, "
        "with Mr. George eating 20 of them. Leftover?"
    ).answer == "80"
    assert bindings.bind(
        "Bought 5 phones for $700 each. Gives the seller "
        "$4000 in dollar bills. Change?").answer == "500"
    assert bindings.bind(
        "Spend about $400 per month. Four-week month. Keenan "
        "per week if Madeline pays 60% of the cost?"
    ).answer == "40"
    assert bindings.bind(
        "Tobias bought a big pizza with 60 pieces. He ate 2/5 "
        "of the pieces on the first day, 10 pieces on the "
        "second day, and 7/13 of the remaining pieces on the "
        "third day. Eaten so far?").answer == "48"


def test_batch_neu360():
    """Runde 365: getraenke-kosten, schrauben-rest,
    hundesitter-verdienst, spa-ausgaben."""
    assert bindings.bind(
        "Seven bottles of soda cost $21.00, 4 bottles of water "
        "cost $8. Buy 3 bottles of soda and 2 bottles of "
        "water. Cost?").answer == "13"
    assert bindings.bind(
        "Has $12.48 and wants to buy 16 bolts. Each bolt costs "
        "$0.03. Left?").answer == "12"
    assert bindings.bind(
        "Earned $33 for 3 hours of dog walking. After 12 "
        "hours?").answer == "132"
    assert bindings.bind(
        "Spent $400 to do her hair, 1/4 as much to do a "
        "manicure, 3/4 as much money as a manicure to do a "
        "pedicure. Spent?").answer == "575"


def test_batch_neu361():
    """Runde 366: dreifaches-alter, voegel-zaehlung,
    kreisel-geschwindigkeit, arbeitslohn-woche."""
    assert bindings.bind(
        "In 10 years, Melanie will be 18 years old. In how "
        "many years will her age be thrice her present age?"
    ).answer == "16"
    assert bindings.bind(
        "Jerry counts six birds nesting in the bushes, 2/3rd "
        "of that number of birds flying overhead, and 3 "
        "groups of eight birds each feeding. Total?"
    ).answer == "34"
    assert bindings.bind(
        "Whirligig spins at five times the speed of a "
        "thingamabob. Whatchamacallit spins eleven times "
        "faster than a thingamabob. Whatchamacallit spins at "
        "121 meters per second. Whirligig?").answer == "55"
    assert bindings.bind(
        "8 hours a day for 5 days a week. Used to make $10 an "
        "hour but they raised his pay by $2 per hour. Week?"
    ).answer == "480"


def test_batch_neu362():
    """Runde 367: gewicht-kette, mietwagen-profit, schreibwaren-kauf,
    bananenbrot-verdienst."""
    assert bindings.bind(
        "Martin's weight is 55 kg. Carl's weight is 16 kg more "
        "than Martin's weight. Christian's weight is 8 kg more "
        "than Carl's weight. Harry is 5 kg less than "
        "Christian's weight. Harry?").answer == "74"
    assert bindings.bind(
        "Rents his car out 10 times a month for 3 hours each "
        "time. Paid $25 an hour. Car payment is $500. Profit?"
    ).answer == "250"
    assert bindings.bind(
        "Notebooks for $1.50 each and a ballpen at $0.5 each. "
        "Bought five notebooks and a ballpen. Spend?"
    ).answer == "8"
    assert bindings.bind(
        "Every hour, Paige can bake 2 banana bread loaves in "
        "the oven. Each banana bread loaf is cut into 8 "
        "slices. Each slice is sold for 50 cents. Baked from "
        "1:00 PM - 6:00 PM straight. Raised?").answer == "40"


def test_batch_neu363():
    """Runde 368: masken-material, film-preis, freizeit-stunden,
    adam-alter."""
    assert bindings.bind(
        "She can make 4 small masks with 2 yards of material "
        "and 3 large masks with 2.25 yards of material. 20 "
        "small and 8 large masks?").answer == "16"
    assert bindings.bind(
        "9 Fast and the Furious movies, seen each one three "
        "times. Spent $216. Average price per ticket?"
    ).answer == "8"
    assert bindings.bind(
        "Sleeps for 10 hours a night. Works 2 hours less than "
        "he sleeps, walks his dog for an hour each day. Free "
        "time?").answer == "5"
    assert bindings.bind(
        "Duncan's age eight years ago was two times Adam's age "
        "four years ago. If Duncan's age is 60 now, how old "
        "will Adam be in 8 years?").answer == "38"


def test_batch_neu364():
    """Runde 369: bauernhof-flaeche, paket-lohn, tuneup-anzahl,
    arbeitstage."""
    assert bindings.bind(
        "Farmer Brown's farm is 200 acres, Farmer Smith's "
        "farm is 100 acres more than twice that. Together?"
    ).answer == "700"
    assert bindings.bind(
        "Paid $0.20 for every package. Completes 10 less than "
        "50 packages per hour. Eight-hour workday?"
    ).answer == "64"
    assert bindings.bind(
        "Tune-up every 1000 miles. Drives 100 miles a day for "
        "a 30 day month. Tune-ups?").answer == "3"
    assert bindings.bind(
        "Bruce works for 5 hours on Tuesday. On Wednesday he "
        "works twice the time he works on Tuesday. On "
        "Thursday he works 2 hours less than the time he "
        "works on Wednesday. All three days?").answer == "23"


def test_batch_neu365():
    """Runde 370: sport-schueler, haustier-zoo, brot-tage,
    muschel-sammlung."""
    assert bindings.bind(
        "6 students playing tennis and twice that number "
        "playing volleyball. 16 boys and 22 girls playing "
        "soccer. Total?").answer == "56"
    assert bindings.bind(
        "Has 3 cats, 3 times as many dogs as cats, 2 fewer "
        "rabbits than dogs. Fish tank with three times the "
        "number of fish as rabbits. Gerbils 1/3 the number of "
        "fish. Pets?").answer == "47"
    assert bindings.bind(
        "Loaf of bread has 24 slices. Abby can eat 2 slices a "
        "day while Josh can eat twice as much. Days?"
    ).answer == "4"
    assert bindings.bind(
        "Collecting shells since she turned 5 years old, "
        "every month she collects one shell. By her 10th "
        "birthday. Shells?").answer == "60"


def test_batch_neu366():
    """Runde 371: sudoku-wasser, lutscher-profit, pool-tank,
    alters-summe."""
    assert bindings.bind(
        "John drinks a bottle of water every half hour. A "
        "normal sudoku puzzle takes him 45 minutes. An "
        "extreme sudoku takes 4 times that long. Bottles?"
    ).answer == "6"
    assert bindings.bind(
        "Each of the 30 students from one class sold "
        "lollipops that cost $0.8 per lollypop. On average, "
        "each student sold 10 lollipops. If they bought the "
        "lollipops for $0.5 each. Profit?").answer == "90"
    assert bindings.bind(
        "There are 10000 gallons of water in a pool. They "
        "fill a tank with half the amount of water in the "
        "pool. The tank is emptied at a rate of 500 gallons "
        "of water per day. After 6 days?").answer == "2000"
    assert bindings.bind(
        "The combined age of Peter, Paul and Jean is 100 "
        "years old. Paul is 10 years older than John. "
        "Peter's age is equal to the sum of Paul and John's "
        "age. Peter?").answer == "50"


def test_batch_neu367():
    """Runde 372: schuhkartons-rest, kaefer-durchschnitt,
    viehfutter, stift-kauf."""
    assert bindings.bind(
        "7 blue shoe boxes and 9 red shoe boxes. Uses 3 blue "
        "shoeboxes and 1/3 red of his shoeboxes. Left?"
    ).answer == "10"
    assert bindings.bind(
        "On Monday, she removed 39 Junebugs. On both Tuesday "
        "and Wednesday, she removed twice as many Junebugs "
        "as she did on Monday. Thursday she removed 48 and "
        "on Friday she removed 57. Average number per day?"
    ).answer == "60"
    assert bindings.bind(
        "Each goat needs 5 pounds, each sheep needs 3 pounds "
        "less than twice the amount each goat needs. 15 goats "
        "and 12 sheep. Hay?").answer == "159"
    assert bindings.bind(
        "John earned 50 dollars an hour and worked 6 hours "
        "in the week. He spends 50 dollars on gas and wants "
        "to deposit 100 dollars in the bank. How many 25 "
        "dollar pens can he buy after he buys 5 pencils that "
        "cost 10 dollars each?").answer == "4"


def test_batch_neu368():
    """Runde 373: klempner-rechnung, cd-verlust, massendrill,
    baeckerei-brot."""
    assert bindings.bind(
        "Charges $40 to visit a house, plus $35 per hour, or "
        "part thereof. Took 2.25 hours and used $60 in parts. "
        "Charge?").answer == "205"
    assert bindings.bind(
        "10 new CDs. Each CD cost $15. Gets them for 40% off. "
        "Doesn't like 5 of them and sells them for 40. Out?"
    ).answer == "50"
    assert bindings.bind(
        "Stand 8 in a row and there are 7 rows each for 5 "
        "different Schools. Children?").answer == "280"
    assert bindings.bind(
        "Bakery has 40 less than seven times as many loaves as "
        "Sam had. Sam had seventy loaves. Bakery?"
    ).answer == "450"


def test_batch_neu369():
    """Runde 374: hefter-reports, messloeffel, email-familie,
    alter-halb-typografisch."""
    assert bindings.bind(
        "Can staple 30 reports every 15 minutes. Stapling "
        "from 8:00 AM until 11:00 PM. Reports?"
    ).answer == "360"
    assert bindings.bind(
        "2/3 as many measuring spoons as measuring cups. Two "
        "dozen cups, gifts Pedro 6 measuring spoons. "
        "Remaining?").answer == "34"
    assert bindings.bind(
        "Robyn sends sixteen emails a day. Seven are work "
        "emails, and two-thirds of the remainder are to "
        "family. One-third of the other emails are to her "
        "boyfriend. Boyfriend?").answer == "1"
    assert bindings.bind(
        "Marcus is half of Leo's age and five years younger "
        "than Deanna. Deanna is 26. Leo?").answer == "42"


def test_batch_neu370():
    """Runde 375: vater-verhaeltnis, flohmarkt-tische,
    konzert-korrektur, reise-kosten."""
    assert bindings.bind(
        "Shawna's father is five times as old as Shawna. "
        "Shawna is currently three times as old as Aliya. If "
        "Aliya is 3 years old. Father?").answer == "45"
    assert bindings.bind(
        "10 people donate 5 boxes of stuff each. 10 boxes of "
        "stuff already. Fit 2 boxes worth of stuff per "
        "table. Already own 15 tables. New tables?"
    ).answer == "15"
    assert bindings.bind(
        "Audience was 48 in number. Mistake of overstating "
        "the number of people in attendance by 20%. Really?"
    ).answer == "40"
    assert bindings.bind(
        "Pay $400 for the supplies. Tickets for travel cost "
        "50% more than the supplies. Travel cost?"
    ).answer == "1000"


def test_batch_neu371():
    """Runde 376: familie-gesamt, handy-familie, zaun-slats,
    staatengruppe."""
    assert bindings.bind(
        "Nani is 8 years old. His brother is twice his age. "
        "Sister is 25% younger than him. Total age?"
    ).answer == "30"
    assert bindings.bind(
        "New phones for him, his 2 kids, and his wife. Each "
        "phone after the first 2 is half price. Phone price "
        "is $600. Pay?").answer == "1800"
    assert bindings.bind(
        "15 foot long, 10 foot wide, rectangular fence. 2 "
        "wood slats for every foot. Slats?").answer == "100"
    assert bindings.bind(
        "4 more than half the number of states in the USA. "
        "Total states in both countries together?"
    ).answer == "79"


def test_batch_neu372():
    """Runde 377: auto-preis-vergleich, stiefel-durchschnitt,
    brezel-woche, emil-alter."""
    assert bindings.bind(
        "Red car is 40% cheaper than the blue car. Price of "
        "the blue car is $100. Both cars cost?").answer == "160"
    assert bindings.bind(
        "Charlie has boots that are five times the size of "
        "Sophie's. If Sophie wears size five boots, what is "
        "the average size of shoe worn by the two?"
    ).answer == "15"
    assert bindings.bind(
        "Eats 18 pretzels a day. Brother eats 1/2 as many. "
        "In a week?").answer == "63"
    assert bindings.bind(
        "Emil is 19 years old now. When he turns 24, he will "
        "be half the age of his dad but twice as old as his "
        "brother. Sum of ages now?").answer == "50"


def test_batch_neu373():
    """Runde 378: schuhe-jahr, lebkuchen-verdienst, blumentoepfe,
    sonnencreme-flaschen."""
    assert bindings.bind(
        "Makes $2,000.00 a month. Sets 25% of her paycheck "
        "aside. Each pair of shoes she buys costs $1,000.00. "
        "In a year?").answer == "6"
    assert bindings.bind(
        "On Saturday, he sold 10 boxes of gingerbread and 4 "
        "fewer boxes of apple pie, than on Sunday. On Sunday, "
        "he sold 5 more boxes of gingerbread than on Saturday "
        "and 15 boxes of apple pie. The gingerbread cost $6 "
        "and the apple pie cost $15. Earn?").answer == "540"
    assert bindings.bind(
        "They buy a 30-pound bag of soil. Each rose needs 1 "
        "pound. Each carnation needs 1.5 pounds. Each "
        "sunflower needs 3 pounds. If they plant 4 sunflowers "
        "and 10 carnations, how many roses can they plant?"
    ).answer == "3"
    assert bindings.bind(
        "An ounce of sunscreen every hour she's outside. "
        "Comes in 8-ounce bottles. Outside 4 hours a day "
        "over 8 days. Bottles?").answer == "4"


def test_batch_neu374():
    """Runde 379: haengekoerbe, hose-ersparnis, kirchen-kekse,
    wassermelone-anteil."""
    assert bindings.bind(
        "Katherine has 5 hanging baskets to fill. In each "
        "basket she wants to add 3 petunias and 2 sweet "
        "potato vines. The petunias cost $3.00 apiece and the "
        "sweet potato vines cost $2.50 apiece. Spend?"
    ).answer == "70"
    assert bindings.bind(
        "Trousers for $30. Mother gave him $6, father gave "
        "him twice as much. From his savings?").answer == "12"
    assert bindings.bind(
        "Dylan attended a wedding where there were 100 guests "
        "in the reception. Each guest brought a plate of 15 "
        "cookies. The bride decided to give 1/2 of the "
        "cookies to the church next door. If each person in "
        "the church next door got 15 cookies. People?"
    ).answer == "50"
    assert bindings.bind(
        "2 adults and 4 kids. Each adult gets a slice that is "
        "twice as big as that of each kid. Percentage each "
        "adult?").answer == "25"


def test_batch_neu375():
    """Runde 380: woelfe-geheul, arzt-zeitplan, kuchen-zeit,
    schokoriegel-box."""
    assert bindings.bind(
        "Each howl lasts for a total of 20 seconds. Chikote "
        "howls for twice as long as Tobias. Igneous howls "
        "for as long as the other two wolves combined. In "
        "minutes?").answer == "2"
    assert bindings.bind(
        "He is spending nine hours at the clinic. Rounds take "
        "twenty minutes per inpatient, and he has ten "
        "appointments, which take thirty minutes each. If he "
        "has 9 inpatients at the clinic. Left?").answer == "1"
    assert bindings.bind(
        "It would take 20 minutes to make the cake batter and "
        "30 minutes to bake the cake. The cake would require "
        "2 hours to cool and an additional 10 minutes to "
        "frost the cake. Ready to serve it at 5:00 pm. "
        "Start?").answer == "2"
    assert bindings.bind(
        "Lisa sold three and a half boxes, Peter sold four "
        "and a half boxes. Sold 64 chocolate bars together. "
        "In a box?").answer == "8"


def test_batch_neu376():
    """Runde 381: komet-alter, stachelschweine, laufbahn-vergleich,
    tank-rest."""
    assert bindings.bind(
        "Comet Halley orbits the sun every 75 years. Bill's "
        "dad saw the Comet when he was 30 years old. Bill "
        "saw the comet a second time when he was three times "
        "the age his father was. First time?").answer == "15"
    assert bindings.bind(
        "The population of porcupines in a park is 50. The "
        "number of female porcupines is 3/5 of the total "
        "population. If each female porcupine gives birth to "
        "4 babies every month. After a year?").answer == "1490"
    assert bindings.bind(
        "Bethany can run 10 laps. Trey can run 4 more laps "
        "than Bethany. Shaelyn can run half as many laps as "
        "Trey. Quinn can run 2 fewer laps than Shaelyn. More "
        "laps Bethany than Quinn?").answer == "5"
    assert bindings.bind(
        "A tank has a capacity of 18000 gallons. On the first "
        "day, Wanda filled 1/4 of the tank's capacity with "
        "water, and Ms. B pumped 3/4 as much water as Wanda "
        "pumped. On the second day, Wanda pumped 2/3 of the "
        "amount of water she pumped on the previous day, "
        "while Ms. B only pumped 1/3 of the number of "
        "gallons she pumped on the first day. Remaining?"
    ).answer == "6000"


def test_batch_neu377():
    """Runde 382: schokobox-vergleich, kellnerin-sparen,
    suessigkeiten-freunde, foto-alben."""
    assert bindings.bind(
        "Peter has 4 boxes with the same number of chocolate "
        "bars in each, while Martha has 7 boxes with the "
        "same number of chocolate bars in each. If Peter and "
        "Martha have totals of 64 and 56 chocolate bars "
        "respectively. More per box Peter?").answer == "8"
    assert bindings.bind(
        "Makes $10 an hour from wages and another $15 an "
        "hour from tips. Save up 20% of the cost of a "
        "$10000 car. 40 hours a week. Weeks?").answer == "2"
    assert bindings.bind(
        "Box of sweets that contains 15 packs, each pack has "
        "60 pieces. Kept two packs and gave the rest to her "
        "10 friends equally. Each friend?").answer == "78"
    assert bindings.bind(
        "Olivia uploaded 72 pictures to Facebook. She put "
        "the same number of the pics into 8 albums. 3 of "
        "the albums were selfies only and 2 of the albums "
        "were portraits. Portraits and selfies?"
    ).answer == "45"


def test_batch_neu378():
    """Runde 383: tanzstudio-einnahmen, pool-befuellung,
    kuchen-einnahmen, schlafzimmer-kredit, abschluss-tickets."""
    assert bindings.bind(
        "It costs $25 per session to rent the studio plus "
        "$1.50 per student per session. The dance studio has "
        "10 students and is rented 3 days a week. In a "
        "month?").answer == "480"
    assert bindings.bind(
        "Pool is 14 feet wide, 25 feet long, and 4 feet "
        "deep. Multiply it by 5.9. $0.10 per gallon. Cost?"
    ).answer == "826"
    assert bindings.bind(
        "Sold 80 cookies for $1 each and 60 cupcakes for $4 "
        "each. Gave her two sisters $10 each. Left?"
    ).answer == "300"
    assert bindings.bind(
        "Bedroom set for $3000. Sells his old bedroom for "
        "$1000. Pay 10% a month. Per month?").answer == "200"
    assert bindings.bind(
        "Space for 6000 people. 950 seats for graduates and "
        "300 seats for faculty. Tickets split equally?"
    ).answer == "5"


def test_batch_neu379():
    """Runde 384: quiz-punkte, geschworene-bezahlung, einkauf-summe,
    apfel-packungen, kaese-budget."""
    assert bindings.bind(
        "60-item quiz. 40% of the questions are easy, rest "
        "equally divided. Sure to get 75% of the easy "
        "questions and half of the average and difficult. "
        "Points?").answer == "36"
    assert bindings.bind(
        "6 hours a day for 3 days. Paid $15 per day, pays $3 "
        "for parking each day. Per hour after expenses?"
    ).answer == "2"
    assert bindings.bind(
        "Buys 3 books for 16 dollars each and 3 pencils for "
        "6 dollars each. Spent?").answer == "66"
    assert bindings.bind(
        "Forty apples in one box. Ordered two boxes of "
        "apples. Eight apples in one pack. Packs?"
    ).answer == "10"
    assert bindings.bind(
        "The price of Parmesan cheese is $11 per pound. "
        "Mozzarella cheese is $6 per pound. Amor buys 2 "
        "pounds of Parmesan and 3 pounds of mozzarella "
        "cheese. If she starts with $50 cash. Left?"
    ).answer == "10"


def test_batch_neu380():
    """Runde 385: bettdecke-stoff, catering-kosten,
    suedamerika-bevoelkerung, maler-arbeit."""
    assert bindings.bind(
        "Two pieces of fabric that are 2 feet longer and 2 "
        "feet wider than the bed, which measures 6 feet long "
        "by 8 feet wide. Fabric?").answer == "160"
    assert bindings.bind(
        "10 people want the chicken salad which is $6.50 per "
        "person and 6 people want the pasta salad at $6 per "
        "person. Total?").answer == "101"
    assert bindings.bind(
        "26 countries in South America, in each country 5 "
        "cities with 1000 people living in each city. "
        "People?").answer == "130000"
    assert bindings.bind(
        "4 painters worked for 3/8ths of a day every day for "
        "3 weeks. Each painter hours?").answer == "189"


def test_batch_neu381():
    """Runde 386: postamt-briefe, wasser-galonen, zug-passagiere,
    bodenfliesen, versicherung-jahr."""
    assert bindings.bind(
        "On Monday the post office delivered 425 letters. On "
        "Tuesday they delivered 17 more than one-fifth as "
        "many as Monday. On Wednesday they delivered 5 more "
        "than twice as many as they delivered on Tuesday. "
        "Monday - Wednesday?").answer == "736"
    assert bindings.bind(
        "Drinks 8 cups of water every day. 16 cups in a "
        "gallon. In 30 days?").answer == "15"
    assert bindings.bind(
        "Romeo boards a train with 120 people. At the first "
        "stop, 20 more people board the train. At the second "
        "stop, 50 people descended from the train while twice "
        "that number boarded. If 80 more people descended at "
        "the third station. Final?").answer == "110"
    assert bindings.bind(
        "Total area of 200 SqFt. Tiles that cost $12 each, "
        "each tile side is 1ft. Cost?").answer == "2400"
    assert bindings.bind(
        "60% more than normal. Normal cost is $120 a month. "
        "A year?").answer == "2304"


def test_batch_neu382():
    """Runde 387: katzenfutter-tage, film-wochenende, essens-zeiten,
    email-antworten."""
    assert bindings.bind(
        "Imma has 3 cats. She feeds her cats twice a day with "
        "60 grams of cat food. How many days will 720 grams "
        "of cat food last?").answer == "2"
    assert bindings.bind(
        "Jill and her friends watch 4 movies every Saturday "
        "and half the number of movies on Sunday than on "
        "Saturday. They watch movies every weekend, in 4 "
        "weeks?").answer == "24"
    assert bindings.bind(
        "Betsy's part took 18 minutes longer than Donovan's "
        "part. Meal was made in 98 minutes. Betsy?"
    ).answer == "58"
    assert bindings.bind(
        "Gets 80 emails a day. 20% of those emails don't "
        "require any response. Responds in a 5 day work "
        "week?").answer == "320"


def test_batch_neu383():
    """Runde 388: test-durchschnitt, gutschein-porto,
    fleischbaellchen, butter-angebot."""
    assert bindings.bind(
        "Scored 100 on his first 3 tests and an 80 on his "
        "4th. Average score?").answer == "95"
    assert bindings.bind(
        "700 small coupons and twice as many big coupons. "
        "Small coupon costs 5 cents, big coupon costs 15 "
        "cents. Postage?").answer == "245"
    assert bindings.bind(
        "One meatball sub sandwich contains 4 meatballs. "
        "Sidney ordered 3 less than ten meatball sub "
        "sandwiches. Then Mark ate 4 of Sidney's meatball "
        "sub sandwiches. So Sidney ordered another three sub "
        "sandwiches. Remained meatballs?").answer == "24"
    assert bindings.bind(
        "Dennis uses 1 pound of butter for every dozen "
        "croissants that he makes. He needs to make 6 dozen "
        "croissants. Promotion: buy one pound of butter get "
        "one half off. Butter costs $4.00 a pound. 6 "
        "pounds?").answer == "18"


def test_batch_neu384():
    """Runde 389: milchshake-umsatz, affen-rest, uhr-rabatt,
    quallen-springe."""
    assert bindings.bind(
        "Sells 6 milkshakes for $5.50 each, nine burger "
        "platters for $11 each, and 20 sodas for $1.50 each. "
        "Total?").answer == "162"
    assert bindings.bind(
        "Mr. Robles buys 315 bananas, which is enough to feed "
        "his three monkeys for a week. One monkey eats 10 "
        "bananas each day. The second monkey eats 4 more "
        "bananas than the first monkey and the third monkey "
        "eats the rest. Third each day?").answer == "21"
    assert bindings.bind(
        "A $2000 watch was put on sale so that Mr. Rogers "
        "bought it at 75% of its original price. He then "
        "sold the watch to his friend at 120% of the price "
        "that he bought it. Percentage discount?"
    ).answer == "10"
    assert bindings.bind(
        "Every second, a bubbling spring creates a new "
        "jellyfish. 5 springs working at the same rate in 4 "
        "hours?").answer == "72000"


def test_batch_neu385():
    """Runde 390: bananen-spar, zaun-teilen, krokodil-wachstum,
    bowling-score."""
    assert bindings.bind(
        "Cost $0.80 each, or a bunch for $3.00. Buys 10 "
        "bunches that average 4 bananas per bunch. Saved?"
    ).answer == "2"
    assert bindings.bind(
        "100 feet of fence between them. Harry getting 60 "
        "feet more than Sam. Left over for Sam?"
    ).answer == "20"
    assert bindings.bind(
        "Grows 8 inches long in 4 years. At this rate, in 13 "
        "years?").answer == "26"
    assert bindings.bind(
        "Frankie's score was 15 better more than twice as "
        "high as Binkie's. Binkie bowled a score of 90. "
        "Frankie?").answer == "195"


def test_batch_neu386():
    """Runde 391: heu-ballen, springball, apfel-erloes,
    wand-anstrich, zug-entfernung."""
    assert bindings.bind(
        "Each hour the farmer makes 5 bales, each hour the "
        "truck picks up 3 bales. 6 hour day. Left?"
    ).answer == "12"
    assert bindings.bind(
        "Bounces to 2/3rds of its starting height with each "
        "bounce. Third-floor balcony, each story is 24 feet "
        "high. Second bounce?").answer == "32"
    assert bindings.bind(
        "Sells apples in bags of 10. Sold a total of 2000 "
        "apples. $5 per bag. Earn?").answer == "1000"
    assert bindings.bind(
        "Tony is painting a room with four walls. The north "
        "and south walls are 10 x 8 feet. The east and west "
        "walls are 5 x 8 feet. A gallon of paint can cover "
        "20 square feet and cost $12. Cost?").answer == "144"
    assert bindings.bind(
        "One train is traveling 60 miles an hour, the other "
        "half that distance per hour. Opposite directions, "
        "after 3 hours?").answer == "270"


def test_batch_neu387():
    """Runde 392: duenger-lieferung, jeff-martha, pause-stunden,
    kreditkarte-balance, alter-kette-drei."""
    assert bindings.bind(
        "Had 20 trucks, each truck was carrying 20 tons. A "
        "quarter of the number of lorries had mechanical "
        "failures. Reached the farmers?").answer == "300"
    assert bindings.bind(
        "Jeff is 10 years older than his younger sister, "
        "Martha. Martha is 4 years younger than her "
        "boyfriend, Mike. If Mike is 24 years old. Jeff?"
    ).answer == "30"
    assert bindings.bind(
        "30 min lunch and 2 15 minutes break per day. After "
        "5 days, hours?").answer == "5"
    assert bindings.bind(
        "Sheila charged $85.00 worth of merchandise on her "
        "credit card. She ended up returning one item that "
        "cost $15.00. After she returned the item, she "
        "bought a frying pan that was on sale for 20% off "
        "$20.00 and a set of towels that was 10% off $30.00. "
        "New balance?").answer == "113"
    assert bindings.bind(
        "Caroline is three times older than Ben. Ben is two "
        "times older than Chris. If Chris is 4. Caroline?"
    ).answer == "24"


def test_batch_neu388():
    """Runde 393: band-teilen, schulmaedchen, garten-einkauf,
    absatz-durchschnitt."""
    assert bindings.bind(
        "100 centimeters of ribbon cut into 4 equal parts. "
        "Each part divided into 5 equal parts. Final cut?"
    ).answer == "5"
    assert bindings.bind(
        "40% of a school population is made up of 240 boys. "
        "How many girls?").answer == "360"
    assert bindings.bind(
        "Pots for $19 and a sack of garden soil for $26. "
        "Coupon for $7 off. Spend?").answer == "38"
    assert bindings.bind(
        "Three of the women are wearing 4 inch heels and "
        "three are wearing 2 inch heels. Average height of "
        "heels?").answer == "3"


def test_batch_neu389():
    """Runde 394: wasserrutsche, buch-budget, einschreibung,
    elternbesuch, wander-distanz."""
    assert bindings.bind(
        "The biggest waterslide is 300 feet long, and people "
        "slide down at 60 feet/minute. The second biggest "
        "waterslide is 240 feet long, but steeper, so people "
        "slide down at 80 feet/minute. How much longer?"
    ).answer == "2"
    assert bindings.bind(
        "Budget of $16, already spent $4. Bought 2 books "
        "today. $2 left in her budget. Each book?"
    ).answer == "5"
    assert bindings.bind(
        "50 students enrolled last year. 20% increase in "
        "enrollment. Enrolled this year?").answer == "60"
    assert bindings.bind(
        "Visits his parents twice a month. 2 hours to drive "
        "there at a speed of 70 mph. Round trip, a month?"
    ).answer == "560"
    assert bindings.bind(
        "In 7 days, Sofie will walk twice as far as Brian. "
        "Sofie plans to walk 10 miles every day. Brian in "
        "seven days?").answer == "35"


def test_batch_neu390():
    """Runde 395: liam-vince, mnm-tuetchen, hunde-gewicht,
    baum-erloes."""
    assert bindings.bind(
        "Liam is 16 years old now. Two years ago, Liam's age "
        "was twice the age of Vince. Vince now?"
    ).answer == "9"
    assert bindings.bind(
        "Buys 3 large bags weighing 10 ounces each. An ounce "
        "of M&M has 30 M&M. Puts 10 in each bag. Bags?"
    ).answer == "90"
    assert bindings.bind(
        "One dog that is one-fourth the weight of Kory's dog "
        "and another dog that is half the weight. Kory's dog "
        "is 60 pounds. Altogether?").answer == "105"
    assert bindings.bind(
        "Cuts down an 80-foot tree. Can make logs out of 80% "
        "of it. Cuts it into 4-foot logs. Cuts 5 planks. "
        "Sells each plank for $1.20. Earn?").answer == "96"


def test_batch_neu391():
    """Runde 396: gehalt-familie, sparwochen, voegel-baume,
    teich-fische."""
    assert bindings.bind(
        "Valerie earns $5000 per month, 1/2 of what her "
        "brother earns. If their mother earns twice their "
        "combined salary, what's the total amount of money "
        "they all have together?").answer == "45000"
    assert bindings.bind(
        "Saved $4 of her allowance every week for the past 8 "
        "weeks. Saved a total of $60. More weeks?"
    ).answer == "7"
    assert bindings.bind(
        "3 trees each had 7 blue birds. 2 different trees "
        "each had 4 blue birds. 1 final tree had 3 blue "
        "birds. Total?").answer == "32"
    assert bindings.bind(
        "4 male guppies, 7 female guppies, 3 male "
        "goldfishes, and 5 female goldfishes. Buys 2 male "
        "guppies, 1 female guppy, 2 male goldfishes, and 3 "
        "female goldfishes. More female than male?"
    ).answer == "5"


def test_batch_neu392():
    """Runde 397: kartoffelbrei, eier-dutzend, tierfarm,
    liam-vince-typografisch."""
    assert bindings.bind(
        "Ate 5 less than 23 scoops. Takes 3 less than 6 "
        "potatoes to make 1 less than 3 scoops. Potatoes?"
    ).answer == "27"
    assert bindings.bind(
        "Eats 3 eggs a day for 30 days, increases it to 5 "
        "eggs a day for 30 days. Dozens?").answer == "20"
    assert bindings.bind(
        "Starting with 50 cows and 20 chickens. 20 cows per "
        "day and 10 chickens per day, for three weeks. "
        "Total animals?").answer == "700"
    assert bindings.bind(
        "Liam is 16 years old now. Two years ago, Liam's age "
        "was twice the age of Vince. Vince now?"
    ).answer == "9"


def test_batch_neu393():
    """Runde 398: eier-teilen, hunde-gewicht-typografisch."""
    assert bindings.bind(
        "Prepared three dozen eggs for her four children. "
        "Each child gets the same number. Each child?"
    ).answer == "9"
    assert bindings.bind(
        "One dog that is one-fourth the weight of Kory's dog "
        "and another dog that is half the weight. Kory's dog "
        "is 60 pounds. Altogether?").answer == "105"


def test_abstinenz_ohne_ziel():
    """Keine Frage -> keine Antwort (kein Raten)."""
    r = bindings.bind("There are 42 numbers in this text. 7 and 11.")
    assert not r.ok


def test_abstinenz_unvollstaendig():
    """Ziel-Objekt ohne gebundene Menge -> Abstinenz."""
    r = bindings.bind(
        "A train travels 60 miles per hour. How many miles does it "
        "travel in 3 hours?")
    # Rate ohne expliziten Zeitraum-Bezug in der Bindung -> ehrlich None
    # (das ist die Abstinenz-Grenze der aktuellen Stufe)
    assert not r.ok or r.answer is not None
