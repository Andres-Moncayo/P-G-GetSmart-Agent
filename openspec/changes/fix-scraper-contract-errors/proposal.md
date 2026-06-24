## Why

El contrato actual del scraper (scraper_contract.yaml y scraper_contract.md) contiene errores de validación que impiden el correcto funcionamiento del flujo de OpenSpec. Estos errores necesitan ser corregidos para asegurar que las especificaciones del scraper cumplan con los estándares del proyecto y puedan ser utilizados correctamente en el workflow de desarrollo.

## What Changes

Se corregirán los errores de validación en los siguientes archivos:
- openspec/specs/scraper/scraper_contract.yaml
- openspec/specs/scraper/scraper_contract.md

Las correcciones incluirán:
- Validaciones de esquema YAML
- Correcciones de sintaxis en los contratos
- Alineación con los estándares de especificación del proyecto
- Asegurar consistencia entre el archivo YAML y su documentación Markdown

## Capabilities

### Modified Capabilities
- `scraper-contract`: Corrección de errores de validación en especificaciones del scraper para asegurar cumplimiento del workflow de OpenSpec

## Impact

- Especificaciones del scraper reparadas
- Mejora de la validez de los contratos de especificación
- Habilitación del workflow completo de OpenSpec para el módulo scraper
- Sin cambios en el código de implementación, solo en las especificaciones