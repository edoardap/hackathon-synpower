A causa do 500 é `None * int` levantando `TypeError`. Correção no endpoint:

```python
@router.post("/opportunities")
def create(op: OpportunityIn, db=Depends(get_db), org=Depends(current_org)):
    total = None if op.amount is None or op.quantity is None else op.amount * op.quantity
    row = Opportunity(org_id=org.id, name=op.name, total=total)
    db.add(row); db.commit()
    return row
```

Premissa: oportunidade sem valor é legítima (ainda em prospecção), então `total` fica nulo. Isso exige a coluna `total` nullable. Se não for, use `total=0` no lugar de `None`.

Se `amount` for obrigatório pelo negócio, o certo é rejeitar com 422 em vez de aceitar: no schema, troque `amount: Optional[Decimal]` por `amount: Decimal`. Aí o Pydantic devolve o erro sozinho e o endpoint fica como estava.

Não mexi em mais nada: sem refactor, sem camada nova. Vale conferir se outros pontos que leem `total` (listagens, somatórios no frontend) toleram nulo.
