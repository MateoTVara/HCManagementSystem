package com.hcmanagement.service;

import com.itextpdf.kernel.pdf.*;
import com.itextpdf.layout.*;
import com.itextpdf.layout.element.*;
import org.springframework.stereotype.Service;

import java.io.ByteArrayOutputStream;
import java.util.List;
import java.util.Map;

@Service
public class DiseasePdfService {
    public byte[] generateDiseasesPdf(List<Map<String, Object>> diseases) throws Exception {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        PdfWriter writer = new PdfWriter(baos);
        PdfDocument pdf = new PdfDocument(writer);
        Document document = new Document(pdf);

        document.add(new Paragraph("Reporte de Enfermedades Más Frecuentes").setBold().setFontSize(16));
        document.add(new Paragraph(" "));

        Table table = new Table(new float[]{4, 8, 4});
        table.addHeaderCell("Código");
        table.addHeaderCell("Nombre");
        table.addHeaderCell("Cantidad");

        for (Map<String, Object> disease : diseases) {
            table.addCell(disease.getOrDefault("code_4", "").toString());
            table.addCell(disease.getOrDefault("name", "").toString());
            table.addCell(disease.getOrDefault("count", "0").toString());
        }

        document.add(table);
        document.close();
        return baos.toByteArray();
    }
}