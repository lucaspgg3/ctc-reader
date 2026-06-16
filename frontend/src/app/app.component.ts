import { Component } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { CtcReaderService } from './services/ctc-reader.service';
import { ResponseLeituraCTC } from './models/ctc.model';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  arquivoSelecionado: File | null = null;
  carregando = false;
  erro: string | null = null;
  resultado: ResponseLeituraCTC | null = null;

  constructor(private ctcReader: CtcReaderService) { }

  onArquivoSelecionado(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.arquivoSelecionado = input.files?.[0] ?? null;
    this.resultado = null;
    this.erro = null;
  }

  enviar(): void {
    if (!this.arquivoSelecionado) {
      return;
    }
    this.carregando = true;
    this.erro = null;
    this.resultado = null;
    this.ctcReader.lerCTC(this.arquivoSelecionado).subscribe({
      next: (resposta) => {
        this.resultado = resposta;
        this.carregando = false;
      },
      error: (err: HttpErrorResponse) => {
        this.erro = err.error?.detail ?? 'Falha ao processar o arquivo. Verifique se o back-end está rodando.';
        this.carregando = false;
      }
    });
  }
}
