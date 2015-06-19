        .ORG    $0000   ; execution starts at 0
        LDI     R0, $0  ; initialize the stack
        LDSP    R0
        BRA     start   ; jumps to main routine

        .ORG    $100
start   LDI     R0, $0  ; R0 <- $0 (immediate)
        LDI     R1, $1  ; R1 <- $1 (immediate)

loop    CMI     R1, $D  ; R1 - D
        BRZ     done    ; branch if R1 == D (R1 == 13)
        ADD     R0, R1  ; R0 <- R0 + R1
        ADD     R1, R0  ; R1 <- R1 + R0
        BRA     loop    ; branch always ("go to")

done    STOP            ; all done