#!/usr/bin/env bash

set -e

echo "========================================"
echo " Validação do projeto jc-sre-netprobe"
echo "========================================"

echo
echo "[1/4] Executando Ruff..."
ruff check .

echo
echo "[2/4] Executando Mypy..."
mypy src tests

echo
echo "[3/4] Executando testes..."
pytest -v

echo
echo "[4/4] Executando testes com cobertura..."
pytest --cov=jc_sre_netprobe --cov-report=term-missing

echo
echo "========================================"
echo " Todas as validações foram concluídas!"
echo "========================================"
