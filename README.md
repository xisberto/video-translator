# Video Translator

Trabalho 4 da disciplina Computação em Nuvem do PPGIA da Unifor, turma 2023.2.

## Membros da Equipe

- Humberto Fraga
- Moesio Medeiros

## Preparo do ambiente de desenvolvimento

Usar o cloudformation para criar os recursos necessários:

```bash
aws cloudformation deploy --template-file resources.json --stack-name video-rek --capabilities CAPABILITY_IAM
```

Criar e ativar o ambiente virtual:

```bash
python -m venv .venv
. .venv/bin/activate
```

Executar o script `recordresources.py` para armazenar os recursos criados no `config.json` do chalice (usar o mesmo 
`stack-name` informado acima):

```bash
python recordresources.py --stack-name video-rek
```


