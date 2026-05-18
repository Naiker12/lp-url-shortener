# lp-url-shortener

Servicio serverless para acortar URLs con Python 3.12, AWS Lambda, API Gateway HTTP API, DynamoDB y Terraform.

## Endpoint

`POST /shorten`

Body:

```json
{
  "url": "<URL_LARGA>"
}
```

Respuesta exitosa:

```json
{
  "code": "<CODIGO>",
  "short_url": "<URL_CORTA>",
  "url_original": "<URL_LARGA>"
}
```

## Validar antes de deploy

```powershell
python -m venv .venv
pip install -r requirements.txt
$env:DYNAMODB_TABLE="urls"
$env:BASE_URL="<URL_PUBLICA>"
python -m unittest discover tests
```

## Deploy

```bash
terraform validate
terraform init
terraform plan
terraform apply
terraform destroy
terraform output api_endpoint
```

Antes de aplicar, edita `terraform.tfvars` y ajusta `base_url` con el dominio publico que quieres usar para construir `short_url`.

## Probar en Postman online

Usa el valor de `api_endpoint` que entrega Terraform y agrega `/shorten`.

- Collection: `LP URL Shortener`
- Request: `POST Shorten URL`
- Method: `POST`
- URL: `https://TU_API_GATEWAY/shorten`
- Header: `Content-Type: application/json`
- Body raw JSON:

```json
{
  "url": "<URL_LARGA>"
}
```

Terraform crea:

- Lambda Python 3.12.
- IAM role con permisos minimos de logs y DynamoDB.
- Ruta `POST /shorten` en API Gateway HTTP API.
- Stage `$default`.
- Tablas DynamoDB `urls` y `url_stats`.

## Variables

- `DYNAMODB_TABLE`: tabla DynamoDB usada por el repositorio.
- `BASE_URL`: base publica para construir `short_url`.
