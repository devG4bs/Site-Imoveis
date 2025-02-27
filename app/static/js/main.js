// Carregar imóveis
document.addEventListener('DOMContentLoaded', function() {
    carregarImoveis();
    
    // Adicionar evento de clique global para os cards
    document.addEventListener('click', function(e) {
        const cardElement = e.target.closest('.imovel-card');
        if (cardElement && !e.target.closest('button') && !e.target.closest('a')) {
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
            container.innerHTML = '';
            
            if (imoveis.length === 0) {
                container.innerHTML = '<div class="col-12 text-center mt-5"><h3>Nenhum imóvel encontrado</h3></div>';
                return;
            }
            
            imoveis.forEach(imovel => {
                const card = document.createElement('div');
                card.className = 'col-md-4 mb-4';
                
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
                
                // Criar carrossel de fotos
                let carouselId = `carousel-${imovel.id}`;
                let fotosHTML = '';
                
                if (imovel.fotos && imovel.fotos.length > 0) {
                    fotosHTML = `
                        <div id="${carouselId}" class="carousel slide" data-bs-ride="false" data-bs-interval="false">
                            <div class="carousel-inner">`;
                    
                    imovel.fotos.forEach((foto, index) => {
                        fotosHTML += `
                            <div class="carousel-item ${index === 0 ? 'active' : ''}">
                                <img src="/uploads/imoveis/${imovel.id}/${foto}" class="d-block w-100" alt="${imovel.titulo}" style="height: 200px; object-fit: cover;">
                            </div>`;
                    });
                    
                    fotosHTML += `
                            </div>`;
                    
                    if (imovel.fotos.length > 1) {
                        fotosHTML += `
                            <button class="carousel-control-prev" type="button" data-bs-target="#${carouselId}" data-bs-slide="prev" onclick="event.stopPropagation();">
                                <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                                <span class="visually-hidden">Anterior</span>
                            </button>
                            <button class="carousel-control-next" type="button" data-bs-target="#${carouselId}" data-bs-slide="next" onclick="event.stopPropagation();">
                                <span class="carousel-control-next-icon" aria-hidden="true"></span>
                                <span class="visually-hidden">Próximo</span>
                            </button>`;
                    }
                    
                    fotosHTML += `</div>`;
                } else {
                    fotosHTML = `<div class="text-center p-5 bg-light">Sem fotos</div>`;
                }
                
                // Criar o card como um link <a> para garantir o redirecionamento
                card.innerHTML = `
                    <a href="/imoveis/${imovel.id}/detalhes" class="text-decoration-none text-dark">
                        <div class="card imovel-card" style="cursor: pointer;" data-id="${imovel.id}">
                            ${etiquetaHTML}
                            <div class="position-relative">
                                ${fotosHTML}
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
                        </div>
                    </a>
                    <div class="card-footer d-flex justify-content-between mt-n2">
                        <a href="/imoveis/${imovel.id}/detalhes" class="btn btn-sm btn-primary">
                            <i class="fas fa-eye"></i> Ver Detalhes
                        </a>
                        <a href="/imoveis/${imovel.id}/pdf" target="_blank" class="btn btn-sm btn-outline-secondary">
                            <i class="fas fa-file-pdf"></i> PDF
                        </a>
                        <button class="btn btn-sm btn-outline-danger" onclick="excluirImovel(${imovel.id})">
                            <i class="fas fa-trash"></i> Excluir
                        </button>
                    </div>
                `;
                
                container.appendChild(card);
                
                // Inicializar o carrossel após adicionar ao DOM
                if (imovel.fotos && imovel.fotos.length > 0) {
                    const carousel = new bootstrap.Carousel(document.getElementById(carouselId), {
                        interval: false,
                        wrap: true,
                        touch: false
                    });
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