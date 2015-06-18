
start       LDI R0, $0ADC;
            MOV R2, R0;
            LSHR R2;
            LSHR R2;
            LSHL R2;
            LSHL R2;
            CMR R2, R0;
            BRZ negate;
bad0        LDI R7, $BAD0;
            STOP;
negate      MOV R2, R0;
            MOV R3, R0;
            NEG R2;
            NOT R3;
            LDI R4, $FFFF;
            SUB R3, R4; R3 -= -1
            CMR R3, R2;
            BRZ test_xor;
bad1        LDI R7, $BAD1;
            STOP;
test_xor    MOV R2, R0;
            MOV R3, R0;
            XOR R2, R3;
            BRZ mem;
bad2        LDI R7, $BAD2;
            STOP;
mem         MOV R2, R0;
            STA $1000, R2;
            LDA R2, $1000;
            CMR R2, R0;
            BRZ test_rol;
bad3        LDI R7, $BAD3;
            STOP;
test_rol    LDI R3, $8000;
            ROL R3;
            BRC rol_next; take branch
bad4        LDI R7, $BAD4;
            STOP;
rol_next    LDI R3, $7FFF;
            ROL R3;
            BRC bad4; branch not taken
brv_A       LDI R1, $FFFF;
            LDI R2, $7FFF;
            AND R1, R2;
            ADD R2, R1;
            BRV brv_B; branch taken
bad5        LDI R7, $BAD5;
            STOP;
brv_B       DECR R1;
            BRV bad5; branch not taken
sp          LDI R1, $BEEF;
            STSP R2;
            INCR R2;
            STSF R1, $1;
            LDR R3, R2;
            CMR R3, R1;
            BRZ test_ashr;
bad6        LDI R7, $BAD6;
            STOP;
test_ashr   LDI R2, $8000;
            MOV R3, R2;
            ASHR R2;
            AND R3, R2;
            BRZ bad6;
done        LDI R7, $1337;
            STOP;
