.data
iter	word	?

_x00	DD		0.0
		DD		0.0
		DD		0.0
		DD		0.0

_x80	DD		128.0
		DD		128.0
		DD		128.0
		DD		128.0

_xff	DD		255.0
		DD		255.0
		DD		255.0
		DD		255.0

_dat	DD		?
		DD		?
		DD		?
		DD		?

point	QWORD	?

.code
create_LUT_array proc EXPORT
		mov			iter,			0					; zerowanie iteratora
		movups		xmm1,			[rdx]				; wspolczynnik alpha [1.0 - 3.0]
		movups		xmm2,			[_x00]				; 0
		movups		xmm3,			[_x80]				; 128
		movups		xmm4,			[_xff]				; 255
		mov			point,			rcx					; wskaznik na tablice bytow

petla:
		cmp			iter,			256					; czy przerobiono 256 liczb?
		jae			koniec								; jesli tak - koniec
		movups		xmm0,			[rcx]				; wpisz do xmm0 spakowane 4 floaty z pamieci
		subps		xmm0,			xmm3				; odejmij od nich 128
		mulps		xmm0,			xmm1				; pomnoz je przez wspolczynnik alpha
		addps		xmm0,			xmm3				; dodaj do nich 128
		movups		[_dat],			xmm0				; zapisz wynik do zmiennej

		cmpps		xmm0,			xmm2,	1			; sprawdz, czy ktoras z wartosci jest mniejsza od 0 (wpisze NaN jesli jest mniejsza - NaN != 0)
		movmskps	eax,			xmm0				; wpisz maske xmm0 do eax, jesli w xmm0 bylo gdzies NaN, to maska != 0
		cmp			eax,			0					; jesli w eax nie jest 0, ozancza to, ze przynajmniej jedna wartosc w xmm0 byla mniejsza od 0
		ja			xOO									; jesli eax wieksze od 0 popraw wartosci w xmm0 na niemniejsze od 0

		movups 		xmm0,			[_dat]				; odzyskaj wynik ze zmiennej _dat do xmm0
		
		cmpps 		xmm0,			xmm4,	6			; sprawdz, czy ktoraj z wartosci w xmm0 jest wieksza od 255 (wpisze NaN jesli jest wieksza - NaN != 0)
		movmskps	eax,			xmm0				; wpisz maske xmm0 do eax, jesli w xmm0 bylo gdzies NaN, to maska != 0
		cmp			eax,			0					; jesli w eax nie jest 0, oznacza to, ze przynajmniej jedna wartosc w xmm0 byla wieksza od 255
		ja			xff									; jesli eax wieksze od 0 popraw wartosci w xmm0 na niewieszke niz 255
		
		movups 		xmm0,			[_dat]				; odzyskaj wynik ze zmiennej _dat do xmm0
dalej:	
		roundps		xmm0,			xmm0,	1b			; zaokraglij wynik w dol do pelnej liczby calkowitej
		movups		[rcx],			xmm0				; wpisz wszystkie wartosci z xmm0 do pamieci pod adres rcx

		cvttss2si	eax,			dword ptr [rcx]		; konwersja float -> int_32
		mov			r9,				qword ptr [point]	; przepisanie wskaznika na tablice bytow do r9
		mov			byte ptr [r9],	al					; wpisanie do pamieci byte
		add			point,			1					; przesuniecie wskaznika na byty
		add			rcx,			4					; przesuniecie wskaznika na floaty

		cvttss2si	eax,			dword ptr [rcx]		; jak wyzej
		mov			r9,				qword ptr [point]
		mov			byte ptr		[r9],		al
		add			point,			1
		add			rcx,			4
		
		cvttss2si	eax,			dword ptr [rcx]		; jak wyzej
		mov			r9,				qword ptr [point]
		mov			byte ptr		[r9],		al
		add			point,			1
		add			rcx,			4
		
		cvttss2si	eax,			dword ptr [rcx]		; jak wyzej
		mov			r9,				qword ptr [point]
		mov			byte ptr		[r9],		al
		add			point,			1
		add			rcx,			4

		add			iter,			4					; cztery floaty zostaly przerobione
		jmp			petla								; powtorz dla kolejnych czterech

xOO:	
		movups		xmm0,			[_dat]				; odzyskaj wynik ze zmiennej _dat do xmm0
		MAXPS		xmm0,			xmm2				; wpisz do xmm0 najwieksze wyniki (co najmnije 0.0)
		jmp			dalej

xff:	
		movups		xmm0,			[_dat]				; odzyskaj wynik ze zmiennej _dat do zmm0
		MINPS		xmm0,			xmm4				; wpisz do xmm0 mniejsze wyniki (co najwyzej 255.0)
		jmp			dalej

koniec:	
		sub			rcx,			1024
		sub			point,			256
		mov			rax,			point
		ret

create_LUT_array endp

edit_data proc EXPORT
	mov	rax,	0								; wyzeruj rax
	mov r9, r8									; zapisz ile danych zmienic w r9

petla:
	cmp	r9, 0
	jbe	koniec

	; Kanal R
	mov	al,				byte ptr [rcx]			; al = data[i]
	mov	bl,				byte ptr [rdx + rax]	; bl = LUT[data[i]]
	mov	byte ptr [rcx],	bl						; data[i] = LUT[data[i]]

	; Kanal G
	dec r9
	inc	rcx
	mov	al,				byte ptr [rcx]			; al = data[i]
	mov	bl,				byte ptr [rdx + rax]	; bl = LUT[data[i]]
	mov	byte ptr [rcx],	bl						; data[i] = LUT[data[i]]

	; Kanal B
	dec r9
	inc	rcx
	mov	al,				byte ptr [rcx]			; al = data[i]
	mov	bl,				byte ptr [rdx + rax]	; bl = LUT[data[i]]
	mov	byte ptr [rcx],	bl						; data[i] = LUT[data[i]]

	; Kanal A - pomin
	dec r9
	inc	rcx
	dec r9
	inc	rcx
	jmp	petla

koniec:	sub	rcx, r8
		mov	rax, rcx
		ret
edit_data endp
end