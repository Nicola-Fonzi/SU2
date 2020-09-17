Assumiamo che ci sia un bdf che richiede una soluzione reale modale.

In questo bdf ci deve essere:

ECHO = SORT
DISPLACEMENT(PRINT,PUNCH)=ALL

Il solver utilizzerà f06 per leggere la forma dei modi e il punch per construire le matrici
modali.

la normlizzazione dei modi deve essere a massa unitaria


deve essere anche definito UN solo set che sia quello di interfaccia fluido-struttura.

I nodi per l'interfaccia devono avere tutti uscita nel sistema di riferimento globale

La posizione dei nodi può essere definita in un sistema di riferimento locale, ma questo sistema
deve a sua volta essere definito nel sistema globale.