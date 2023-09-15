(define strlen string-length)

(define (empty? s)
  (= (strlen s) 0))

(define (head s)
  (car (string->list s)))

(define (tail s)
  (list->string (cdr (string->list s))))

(define (lev s1 s2)
  (cond ((empty? s1) (strlen s2))
        ((empty? s2) (strlen s1))
        ((eq? (head s1) (head s2)) (lev (tail s1) (tail s2)))
        (else
         (+ 1 (min (lev s1 (tail s2))
                   (lev (tail s1) s2)
                   (lev (tail s1) (tail s2)))))))
