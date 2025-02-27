// Carregar imóveis
document.addEventListener('DOMContentLoaded', function() {
    carregarImoveis();
    
    // Adicionar evento de clique global para os cards
    document.addEventListener('click', function(e) {
        const cardElement = e.target.closest('.imovel-card');
        if (cardElement && !e.target.closest('a')) {
            const imovelId = cardElement.getAttribute('data-id');
            if (imovelId) {
                window.location.href = `/imoveis/${imovelId}/detalhes`;
            }
        }
    });
});

// Função para carregar imóveis
function carregarImoveis(tipo = null) {
    let url = '/imoveis/';
    if (tipo && tipo !== 'todos') {
        url += `?tipo=${tipo}`;
    }
    
    fetch(url)
        .then(response => response.json())
        .then(imoveis => {
            const container = document.getElementById('imoveisContainer');
            const indicatorsContainer = document.getElementById('carouselImoveisIndicators');
            container.innerHTML = '';
            indicatorsContainer.innerHTML = '';
            
            // Agrupar imóveis em grupos de 3
            const grupos = [];
            for (let i = 0; i < imoveis.length; i += 3) {
                grupos.push(imoveis.slice(i, i + 3));
            }
            
            grupos.forEach((grupo, index) => {
                // Criar indicador
                const indicator = document.createElement('button');
                indicator.type = 'button';
                indicator.setAttribute('data-bs-target', '#carouselImoveis');
                indicator.setAttribute('data-bs-slide-to', index.toString());
                if (index === 0) indicator.classList.add('active');
                indicatorsContainer.appendChild(indicator);

                // Criar slide
                const carouselItem = document.createElement('div');
                carouselItem.className = `carousel-item ${index === 0 ? 'active' : ''}`;
                
                const row = document.createElement('div');
                row.className = 'row';
                
                grupo.forEach(imovel => {
                    const col = document.createElement('div');
                    col.className = 'col-md-4';
                    
                    let etiquetaHTML = '';
                    if (imovel.etiqueta) {
                        let etiquetaClass = '';
                        switch (imovel.etiqueta) {
                            case 'destaque': etiquetaClass = 'bg-warning'; break;
                            case 'novo': etiquetaClass = 'bg-success'; break;
                            case 'exclusivo': etiquetaClass = 'bg-danger'; break;
                        }
                        etiquetaHTML = `<span class="badge ${etiquetaClass} etiqueta">${imovel.etiqueta.toUpperCase()}</span>`;
                    }
                    
                    let tipoLabel = '';
                    switch (imovel.tipo) {
                        case 'venda': tipoLabel = 'Venda'; break;
                        case 'aluguel': tipoLabel = 'Aluguel'; break;
                        case 'leilao': tipoLabel = 'Leilão'; break;
                    }
                    
                    col.innerHTML = `
                        <div class="card imovel-card" data-id="${imovel.id}">
                            ${etiquetaHTML}
                            <div class="position-relative">
                                <img src="${imovel.fotos && imovel.fotos.length > 0 ? `/uploads/imoveis/${imovel.id}/${imovel.fotos[0]}` : '/static/img/no-image.jpg'}" 
                                     class="card-img-top" 
                                     alt="${imovel.titulo}"
                                     style="height: 200px; object-fit: cover;">
                                <span class="badge bg-primary position-absolute bottom-0 start-0 m-2">${tipoLabel}</span>
                            </div>
                            <div class="card-body">
                                <h5 class="card-title">${imovel.titulo}</h5>
                                <p class="card-text text-truncate">${imovel.descricao}</p>
                                <p class="card-text">
                                    <strong>R$ ${imovel.valor.toLocaleString('pt-BR')}</strong>
                                </p>
                                <div class="d-flex justify-content-between">
                                    <span><i class="fas fa-ruler-combined"></i> ${imovel.area}m²</span>
                                    <span><i class="fas fa-bed"></i> ${imovel.quartos}</span>
                                    <span><i class="fas fa-bath"></i> ${imovel.banheiros}</span>
                                    <span><i class="fas fa-car"></i> ${imovel.vagas}</span>
                                </div>
                            </div>
                            <div class="card-footer bg-transparent border-top-0">
                                <a href="/imoveis/${imovel.id}/detalhes" class="btn btn-sm btn-outline-primary w-100">
                                    <i class="fas fa-eye"></i> Ver Detalhes
                                </a>
                            </div>
                        </div>
                    `;
                    
                    row.appendChild(col);
                });
                
                carouselItem.appendChild(row);
                container.appendChild(carouselItem);
            });

            // Inicializar o carrossel
            const carouselElement = document.getElementById('carouselImoveis');
            const carousel = new bootstrap.Carousel(carouselElement, {
                interval: 5000,
                wrap: true,
                touch: true,
                keyboard: true,
                pause: 'hover'
            });

            // Adicionar eventos de clique aos controles
            const prevButton = carouselElement.querySelector('.carousel-control-prev');
            const nextButton = carouselElement.querySelector('.carousel-control-next');

            prevButton.addEventListener('click', (e) => {
                e.preventDefault();
                carousel.prev();
            });

            nextButton.addEventListener('click', (e) => {
                e.preventDefault();
                carousel.next();
            });

            // Adicionar eventos de clique aos indicadores
            const carouselIndicators = carouselElement.querySelectorAll('.carousel-indicators button');
            carouselIndicators.forEach((indicator, index) => {
                indicator.addEventListener('click', (e) => {
                    e.preventDefault();
                    carousel.to(index);
                });
            });

            // Adicionar eventos de teclado
            document.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowLeft') {
                    carousel.prev();
                } else if (e.key === 'ArrowRight') {
                    carousel.next();
                }
            });
        })
        .catch(error => {
            console.error('Erro ao carregar imóveis:', error);
        });
}

// Função para abrir detalhes do imóvel
function abrirDetalhesImovel(event, id) {
    // Redirecionar para a página de detalhes sem condições
    window.location.href = `/imoveis/${id}/detalhes`;
}

// Função para filtrar imóveis
function filtrarImoveis(tipo) {
    carregarImoveis(tipo);
}

// Função para salvar novo imóvel
async function salvarImovel() {
    const form = document.getElementById('imovelForm');
    const formData = new FormData(form);
    
    // Pegar todos os arquivos selecionados
    const fileInput = form.querySelector('input[type="file"]');
    const files = fileInput.files;
    
    // Remover entrada antiga de fotos (se houver)
    formData.delete('fotos');
    
    // Adicionar cada arquivo como uma entrada separada com o mesmo nome
    for (let i = 0; i < files.length; i++) {
        formData.append('fotos', files[i]);
    }
    
    try {
        const response = await fetch('/imoveis', {
            method: 'POST',
            body: formData // Enviar como FormData
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('novoImovelModal'));
            modal.hide();
            form.reset();
            carregarImoveis();
            alert('Imóvel cadastrado com sucesso!');
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erro ao cadastrar imóvel');
        }
    } catch (error) {
        console.error('Erro ao salvar imóvel:', error);
        alert(error.message || 'Erro ao cadastrar imóvel. Por favor, tente novamente.');
    }
}

// Função para excluir imóvel
async function excluirImovel(id) {
    // Verificar se o usuário é administrador
    const isAdmin = localStorage.getItem('isAdmin');
    if (isAdmin !== 'true') {
        alert('Apenas administradores podem excluir imóveis.');
        return;
    }
    
    if (!confirm('Tem certeza que deseja excluir este imóvel?')) {
        return;
    }
    
    try {
        const response = await fetch(`/imoveis/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            carregarImoveis();
            alert('Imóvel excluído com sucesso!');
        } else {
            throw new Error('Erro ao excluir imóvel');
        }
    } catch (error) {
        console.error('Erro ao excluir imóvel:', error);
        alert('Erro ao excluir imóvel. Por favor, tente novamente.');
    }
}

// Função para gerar PDF
async function gerarPDF(id) {
    try {
        window.open(`/imoveis/${id}/pdf`, '_blank');
    } catch (error) {
        console.error('Erro ao gerar PDF:', error);
        alert('Erro ao gerar PDF. Por favor, tente novamente.');
    }
}

// Função para visualizar imóvel
function visualizarImovel(id) {
    // Redirecionar para a página de detalhes
    window.location.href = `/imoveis/${id}/detalhes`;
} 