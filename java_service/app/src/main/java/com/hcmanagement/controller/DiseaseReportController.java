package com.hcmanagement.controller;

import com.hcmanagement.service.DiseasePdfService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
public class DiseaseReportController {

    @Autowired
    private DiseasePdfService diseasePdfService;

    @PostMapping("/generate/diseases/pdf")
    public ResponseEntity<byte[]> generateDiseasesPdf(@RequestBody List<Map<String, Object>> diseases) throws Exception {
        byte[] pdfBytes = diseasePdfService.generateDiseasesPdf(diseases);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_PDF);
        headers.setContentDisposition(ContentDisposition.attachment().filename("enfermedades_frecuentes.pdf").build());

        return new ResponseEntity<>(pdfBytes, headers, HttpStatus.OK);
    }
}