package com.hcmanagement.controller;

import com.hcmanagement.service.PatientExcelService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
public class PatientReportController {

    @Autowired
    private PatientExcelService patientExcelService;

    @PostMapping("/generate/patients/excel")
    public ResponseEntity<byte[]> generatePatientsExcel(@RequestBody List<Map<String, Object>> patients) throws Exception {
        byte[] excelBytes = patientExcelService.generatePatientsExcel(patients);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
        headers.setContentDisposition(ContentDisposition.attachment().filename("pacientes.xlsx").build());

        return new ResponseEntity<>(excelBytes, headers, HttpStatus.OK);
    }

}
