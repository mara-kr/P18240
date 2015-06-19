        .ORG $0000
        LDI R0 $0;
        LDSP R0; initalize stack
        LDI R0, $A; n argument
        LDI R1, $2000; addr argument
        LDI R2, $2; multiple argument
        PUSH R0;
        PUSH R1;
        PUSH R2;
        JSR pows;
        ADDSP $3;
        STOP;

        .ORG $500
pows    PUSH R0; n
        PUSH R1; addr
        PUSH R2; current n
        PUSH R3; current power
        PUSH R4; base argument
        LDSF R0, $8;
        LDSF R1, $7;
        LDSF R4, $6;
        LDI R2, $0;
        LDI R3, $0;
        STR R1, R3;

pows_l  LDR R3, R1;
        INCR R1;
        INCR R2;
        PUSH R4;
        PUSH R3;
        JSR mul; (curr power * base arg)
        ADDSP $2;
        STR R1, R7;
        CMR R2, R0;
        BRN pows_l;

pows_d  POP R4;
        POP R3;
        POP R2;
        POP R1;
        POP R0;
        RTN;

        .ORG $1000
mul     PUSH R0;
        PUSH R1;
        PUSH R2;
        LDSF R0, $5;
        LDSF R1, $4;
        LDI R2, $0;

mul_l   ADD R2, R0;
        DECR R1;
        BRZ mul_d;
        BRN mul_d;
        BRA mul_l;

mul_d   MOV R7, R2;
        POP R2;
        POP R1;
        POP R0;
        RTN;
