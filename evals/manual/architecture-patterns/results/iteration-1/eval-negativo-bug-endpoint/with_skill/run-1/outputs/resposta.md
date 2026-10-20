A skill `architecture-patterns` não se aplica: é um bug pontual, sem decisão de arquitetura. Corrigi direto.

Causa: `op.amount` é `None` e `None * int` levanta `TypeError`, que vira 500.

```python
@router.post("/opportunities")
def create(op: OpportunityIn, db=Depends(get_db), org=Depends(current_org)):
    total = None if op.amount is None or op.quantity is None else op.amount * op.quantity
    row = Opportunity(org_id=org.id, name=op.name, total=total)
    db.add(row); db.commit()
    return row
```

Premissa: oportunidade sem valor definido é válida, então `total` fica `None`. Isso exige a coluna `total` nullable. Se o valor for obrigatório, o certo é um 422: declare `amount: Decimal` (sem `Optional`) no `OpportunityIn` e deixe o código do endpoint como estava.

Não testei, porque não tenho o código do projeto.
