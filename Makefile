.PHONY: help build up down logs test clean

help:
	@echo "银龄精算师 - 开发命令"
	@echo ""
	@echo "make build    - 构建Docker镜像"
	@echo "make up       - 启动所有服务"
	@echo "make down     - 停止所有服务"
	@echo "make logs     - 查看服务日志"
	@echo "make test     - 运行测试"
	@echo "make clean    - 清理容器和卷"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	cd backend && pytest -v

clean:
	docker-compose down -v
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
