        .ORG $0000; initalize and call subroutine with args
        LDI R0, $0;
        LDSP R0; initalize the stack
        LDI R0, $21;
        LDI R1, $48;
        PUSH R0; r0 holds x
        PUSH R1; r1 holds y
        JSR gcd;
        ADDSP $2;
        STOP;

        .ORG $1000;
gcd     PUSH R0; gcd(x,y)
        PUSH R1;
        LDSF R0, $4; R0 holds x
        LDSF R1, $3; R1 holds y
        CMI R1, $0 ; if (y==0)
        BRZ base;

recur   PUSH R0; gcd(x,y) = gcd(y, x % y)
        PUSH R1;
        JSR mod;
        ADDSP $2;
        PUSH R1; (y)
        PUSH R7; x % y
        JSR gcd;
        ADDSP $2;
        POP R1;
        POP R0;
        RTN;

base    MOV R7, R0;
        POP R1;
        POP R0
        RTN;

        .ORG $2000;
mod     PUSH R0; mod(x,y) = x % y
        PUSH R1;
        LDSF R0, $4;
        LDSF R1, $3;

m_loop  SUB R0, R1;
        BRN m_done;
        BRA m_loop;

m_done  ADD R0, R1;
        MOV R7, R0;
        POP R1;
        POP R0;
        RTN;

